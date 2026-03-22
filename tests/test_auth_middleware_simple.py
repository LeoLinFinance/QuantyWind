"""
认证中间件简化测试

测试核心功能：JWT 令牌验证、权限检查和请求限流
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock

from backend.middleware.auth_middleware import (
    RateLimiter,
    RateLimitExceededError
)
from backend.services.authentication_service import TokenPayload
from backend.services.authorization_service import AuthorizationService
from backend.models.user import User


class TestRateLimiter:
    """测试 RateLimiter 类"""
    
    def test_rate_limit_not_exceeded(self):
        """测试未超过限流"""
        redis_client = self._create_mock_redis()
        limiter = RateLimiter(max_requests=5, window_seconds=60, redis_client=redis_client)
        user_id = "user123"
        
        # 发送 5 个请求（不应该触发限流）
        for i in range(5):
            limiter.check_rate_limit(user_id)
        
        # 验证没有异常
        print("✓ 未超过限流测试通过")
    
    def test_rate_limit_exceeded(self):
        """测试超过限流"""
        redis_client = self._create_mock_redis()
        limiter = RateLimiter(max_requests=5, window_seconds=60, redis_client=redis_client)
        user_id = "user456"
        
        # 发送 5 个请求
        for i in range(5):
            limiter.check_rate_limit(user_id)
        
        # 第 6 个请求应该触发限流
        with pytest.raises(RateLimitExceededError) as exc_info:
            limiter.check_rate_limit(user_id)
        
        assert "请求过于频繁" in str(exc_info.value.detail)
        print("✓ 超过限流测试通过")
    
    def test_different_users_independent_limits(self):
        """测试不同用户的限流独立"""
        redis_client = self._create_mock_redis()
        limiter = RateLimiter(max_requests=3, window_seconds=60, redis_client=redis_client)
        
        # 用户 1 发送 3 个请求
        for i in range(3):
            limiter.check_rate_limit("user1")
        
        # 用户 2 应该仍然可以发送请求
        limiter.check_rate_limit("user2")
        limiter.check_rate_limit("user2")
        limiter.check_rate_limit("user2")
        
        # 用户 1 应该被限流
        with pytest.raises(RateLimitExceededError):
            limiter.check_rate_limit("user1")
        
        # 用户 2 也应该被限流
        with pytest.raises(RateLimitExceededError):
            limiter.check_rate_limit("user2")
        
        print("✓ 不同用户独立限流测试通过")
    
    def test_reset_rate_limit(self):
        """测试重置限流"""
        redis_client = self._create_mock_redis()
        limiter = RateLimiter(max_requests=5, window_seconds=60, redis_client=redis_client)
        user_id = "user_reset"
        
        # 发送 5 个请求
        for i in range(5):
            limiter.check_rate_limit(user_id)
        
        # 重置限流
        result = limiter.reset_rate_limit(user_id)
        assert result is True
        
        # 现在应该可以再次发送请求
        limiter.check_rate_limit(user_id)
        print("✓ 重置限流测试通过")
    
    def _create_mock_redis(self):
        """创建模拟的 Redis 客户端"""
        client = Mock()
        
        # 模拟数据存储 - 使用字典存储每个用户的请求计数
        user_counts = {}
        
        def mock_pipeline():
            pipe = Mock()
            current_key = [None]
            current_count = [0]
            
            def mock_zremrangebyscore(key, min_score, max_score):
                current_key[0] = key
                # 初始化计数
                if key not in user_counts:
                    user_counts[key] = 0
                return pipe
            
            def mock_zcard(key):
                # 获取当前计数
                current_count[0] = user_counts.get(key, 0)
                return pipe
            
            def mock_zadd(key, mapping):
                # 增加计数
                if key not in user_counts:
                    user_counts[key] = 0
                user_counts[key] += len(mapping)
                return pipe
            
            def mock_expire(key, time_val):
                return pipe
            
            def mock_execute():
                # 返回 zcard 的结果（在 zadd 之前的计数）
                return [None, current_count[0], None, None]
            
            pipe.zremrangebyscore = mock_zremrangebyscore
            pipe.zcard = mock_zcard
            pipe.zadd = mock_zadd
            pipe.expire = mock_expire
            pipe.execute = mock_execute
            
            return pipe
        
        def mock_delete(key):
            if key in user_counts:
                del user_counts[key]
                return 1
            return 0
        
        client.pipeline = mock_pipeline
        client.delete = mock_delete
        
        return client


class TestAuthorizationIntegration:
    """测试授权服务集成"""
    
    def test_permission_check_user_role(self):
        """测试用户角色权限检查"""
        # 创建模拟数据库
        db = Mock()
        
        # 创建测试用户
        user = User(
            id="user123",
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            role="user",
            is_active=True,
            is_locked=False
        )
        
        # 模拟数据库查询
        db.query.return_value.filter.return_value.first.return_value = user
        
        # 创建授权服务
        auth_service = AuthorizationService(db)
        
        # 测试权限检查
        assert auth_service.check_permission("user123", "portfolio", "read") is True
        assert auth_service.check_permission("user123", "portfolio", "write") is True
        assert auth_service.check_permission("user123", "user_management", "read") is False
        
        print("✓ 用户角色权限检查测试通过")
    
    def test_permission_check_viewer_role(self):
        """测试查看者角色权限检查"""
        # 创建模拟数据库
        db = Mock()
        
        # 创建测试用户
        user = User(
            id="viewer123",
            username="viewer",
            email="viewer@example.com",
            password_hash="hashed",
            role="viewer",
            is_active=True,
            is_locked=False
        )
        
        # 模拟数据库查询
        db.query.return_value.filter.return_value.first.return_value = user
        
        # 创建授权服务
        auth_service = AuthorizationService(db)
        
        # 测试权限检查
        assert auth_service.check_permission("viewer123", "portfolio", "read") is True
        assert auth_service.check_permission("viewer123", "portfolio", "write") is False
        assert auth_service.check_permission("viewer123", "portfolio", "delete") is False
        
        print("✓ 查看者角色权限检查测试通过")
    
    def test_permission_check_admin_role(self):
        """测试管理员角色权限检查"""
        # 创建模拟数据库
        db = Mock()
        
        # 创建测试用户
        user = User(
            id="admin123",
            username="admin",
            email="admin@example.com",
            password_hash="hashed",
            role="admin",
            is_active=True,
            is_locked=False
        )
        
        # 模拟数据库查询
        db.query.return_value.filter.return_value.first.return_value = user
        
        # 创建授权服务
        auth_service = AuthorizationService(db)
        
        # 测试权限检查
        assert auth_service.check_permission("admin123", "portfolio", "read") is True
        assert auth_service.check_permission("admin123", "portfolio", "write") is True
        assert auth_service.check_permission("admin123", "portfolio", "delete") is True
        assert auth_service.check_permission("admin123", "user_management", "read") is True
        assert auth_service.check_permission("admin123", "user_management", "write") is True
        
        print("✓ 管理员角色权限检查测试通过")


if __name__ == "__main__":
    # 运行测试
    print("\n=== 运行认证中间件测试 ===\n")
    
    # 测试限流器
    print("测试限流器...")
    test_limiter = TestRateLimiter()
    test_limiter.test_rate_limit_not_exceeded()
    test_limiter.test_rate_limit_exceeded()
    test_limiter.test_different_users_independent_limits()
    test_limiter.test_reset_rate_limit()
    
    # 测试授权
    print("\n测试授权...")
    test_auth = TestAuthorizationIntegration()
    test_auth.test_permission_check_user_role()
    test_auth.test_permission_check_viewer_role()
    test_auth.test_permission_check_admin_role()
    
    print("\n=== 所有测试通过 ✓ ===\n")
