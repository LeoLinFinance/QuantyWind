"""
认证中间件测试

测试 JWT 令牌验证、权限检查和请求限流功能
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

# 配置 pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

from backend.middleware.auth_middleware import (
    get_current_user,
    require_auth,
    require_permission,
    RateLimiter,
    apply_rate_limit,
    create_rate_limiter,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitExceededError
)
from backend.services.authentication_service import (
    TokenPayload,
    TokenExpiredError,
    InvalidTokenError,
    get_authentication_service
)
from backend.services.authorization_service import AuthorizationService
from backend.models.user import User


class TestGetCurrentUser:
    """测试 get_current_user 函数"""
    
    @pytest.mark.asyncio
    async def test_valid_token(self):
        """测试有效令牌"""
        # 创建模拟的认证服务
        auth_service = Mock()
        payload = TokenPayload(
            user_id="user123",
            username="testuser",
            role="user",
            exp=datetime.utcnow() + timedelta(minutes=30)
        )
        auth_service.verify_token.return_value = payload
        
        # 创建模拟的凭证
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token"
        )
        
        # 调用函数
        result = await get_current_user(credentials, auth_service)
        
        # 验证结果
        assert result == payload
        assert result.user_id == "user123"
        assert result.username == "testuser"
        assert result.role == "user"
        auth_service.verify_token.assert_called_once_with("valid_token")
    
    @pytest.mark.asyncio
    async def test_expired_token(self):
        """测试过期令牌"""
        # 创建模拟的认证服务
        auth_service = Mock()
        auth_service.verify_token.side_effect = TokenExpiredError("令牌已过期")
        
        # 创建模拟的凭证
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="expired_token"
        )
        
        # 调用函数并验证异常
        with pytest.raises(AuthenticationError) as exc_info:
            await get_current_user(credentials, auth_service)
        
        assert "令牌已过期" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """测试无效令牌"""
        # 创建模拟的认证服务
        auth_service = Mock()
        auth_service.verify_token.side_effect = InvalidTokenError("令牌无效")
        
        # 创建模拟的凭证
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token"
        )
        
        # 调用函数并验证异常
        with pytest.raises(AuthenticationError) as exc_info:
            await get_current_user(credentials, auth_service)
        
        assert "令牌无效" in str(exc_info.value.detail)


class TestRequirePermission:
    """测试 require_permission 装饰器"""
    
    @pytest.mark.asyncio
    async def test_permission_granted(self, test_db):
        """测试权限授予"""
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
        test_db.query.return_value.filter.return_value.first.return_value = user
        
        # 创建令牌载荷
        current_user = TokenPayload(
            user_id="user123",
            username="testuser",
            role="user",
            exp=datetime.utcnow() + timedelta(minutes=30)
        )
        
        # 创建被装饰的函数
        @require_permission("portfolio", "read")
        async def test_route(current_user: TokenPayload, db):
            return {"success": True}
        
        # 调用函数
        result = await test_route(current_user=current_user, db=test_db)
        
        # 验证结果
        assert result == {"success": True}
    
    @pytest.mark.asyncio
    async def test_permission_denied(self, test_db):
        """测试权限拒绝"""
        # 创建测试用户（viewer 角色没有 delete 权限）
        user = User(
            id="user123",
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            role="viewer",
            is_active=True,
            is_locked=False
        )
        
        # 模拟数据库查询
        test_db.query.return_value.filter.return_value.first.return_value = user
        
        # 创建令牌载荷
        current_user = TokenPayload(
            user_id="user123",
            username="testuser",
            role="viewer",
            exp=datetime.utcnow() + timedelta(minutes=30)
        )
        
        # 创建被装饰的函数
        @require_permission("portfolio", "delete")
        async def test_route(current_user: TokenPayload, db):
            return {"success": True}
        
        # 调用函数并验证异常
        with pytest.raises(PermissionDeniedError) as exc_info:
            await test_route(current_user=current_user, db=test_db)
        
        assert "没有权限" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_missing_authentication(self, test_db):
        """测试缺少认证信息"""
        # 创建被装饰的函数
        @require_permission("portfolio", "read")
        async def test_route(db):
            return {"success": True}
        
        # 调用函数并验证异常
        with pytest.raises(AuthenticationError) as exc_info:
            await test_route(db=test_db)
        
        assert "缺少认证信息" in str(exc_info.value.detail)


class TestRateLimiter:
    """测试 RateLimiter 类"""
    
    def test_rate_limit_not_exceeded(self, redis_client):
        """测试未超过限流"""
        limiter = RateLimiter(max_requests=5, window_seconds=60, redis_client=redis_client)
        user_id = "user123"
        
        # 发送 5 个请求（不应该触发限流）
        for i in range(5):
            limiter.check_rate_limit(user_id)
        
        # 验证没有异常
        # 如果有异常会在上面的循环中抛出
    
    def test_rate_limit_exceeded(self, redis_client):
        """测试超过限流"""
        limiter = RateLimiter(max_requests=5, window_seconds=60, redis_client=redis_client)
        user_id = "user456"
        
        # 发送 5 个请求
        for i in range(5):
            limiter.check_rate_limit(user_id)
        
        # 第 6 个请求应该触发限流
        with pytest.raises(RateLimitExceededError) as exc_info:
            limiter.check_rate_limit(user_id)
        
        assert "请求过于频繁" in str(exc_info.value.detail)
    
    def test_rate_limit_window_expiry(self, redis_client):
        """测试限流窗口过期"""
        limiter = RateLimiter(max_requests=3, window_seconds=2, redis_client=redis_client)
        user_id = "user789"
        
        # 发送 3 个请求
        for i in range(3):
            limiter.check_rate_limit(user_id)
        
        # 等待窗口过期
        time.sleep(2.1)
        
        # 现在应该可以再次发送请求
        limiter.check_rate_limit(user_id)
        # 如果有异常会在这里抛出
    
    def test_get_remaining_requests(self, redis_client):
        """测试获取剩余请求配额"""
        limiter = RateLimiter(max_requests=10, window_seconds=60, redis_client=redis_client)
        user_id = "user_quota"
        
        # 发送 3 个请求
        for i in range(3):
            limiter.check_rate_limit(user_id)
        
        # 获取剩余配额
        quota = limiter.get_remaining_requests(user_id)
        
        # 验证配额信息
        assert quota["limit"] == 10
        assert quota["remaining"] == 7  # 10 - 3 = 7
        assert "reset" in quota
        assert "reset_datetime" in quota
    
    def test_reset_rate_limit(self, redis_client):
        """测试重置限流"""
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
    
    def test_different_users_independent_limits(self, redis_client):
        """测试不同用户的限流独立"""
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


class TestCreateRateLimiter:
    """测试 create_rate_limiter 函数"""
    
    @pytest.mark.asyncio
    async def test_custom_rate_limiter(self, redis_client):
        """测试自定义限流器"""
        # 创建自定义限流器：每分钟 2 请求
        custom_limiter = create_rate_limiter(max_requests=2, window_seconds=60)
        
        # 创建令牌载荷
        current_user = TokenPayload(
            user_id="custom_user",
            username="testuser",
            role="user",
            exp=datetime.utcnow() + timedelta(minutes=30)
        )
        
        # 发送 2 个请求（不应该触发限流）
        custom_limiter(current_user=current_user)
        custom_limiter(current_user=current_user)
        
        # 第 3 个请求应该触发限流
        with pytest.raises(RateLimitExceededError):
            custom_limiter(current_user=current_user)


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_authentication_flow(self, test_db, redis_client):
        """测试完整的认证流程"""
        # 1. 创建用户
        user = User(
            id="integration_user",
            username="integrationtest",
            email="integration@example.com",
            password_hash="hashed",
            role="user",
            is_active=True,
            is_locked=False
        )
        
        # 模拟数据库查询
        test_db.query.return_value.filter.return_value.first.return_value = user
        
        # 2. 创建令牌载荷
        current_user = TokenPayload(
            user_id="integration_user",
            username="integrationtest",
            role="user",
            exp=datetime.utcnow() + timedelta(minutes=30)
        )
        
        # 3. 测试权限检查
        @require_permission("portfolio", "write")
        async def protected_route(current_user: TokenPayload, db):
            return {"message": "Success"}
        
        result = await protected_route(current_user=current_user, db=test_db)
        assert result == {"message": "Success"}
        
        # 4. 测试限流
        limiter = RateLimiter(max_requests=3, window_seconds=60, redis_client=redis_client)
        
        for i in range(3):
            limiter.check_rate_limit(current_user.user_id)
        
        with pytest.raises(RateLimitExceededError):
            limiter.check_rate_limit(current_user.user_id)


# Pytest fixtures
@pytest.fixture
def test_db():
    """创建测试数据库会话（模拟）"""
    # 创建模拟的数据库会话
    db = Mock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.close = Mock()
    return db


@pytest.fixture
def redis_client():
    """创建模拟的 Redis 客户端"""
    # 创建模拟的 Redis 客户端
    client = Mock()
    
    # 模拟 Redis 数据存储
    data_store = {}
    sorted_sets = {}
    
    def mock_setex(key, time, value):
        data_store[key] = value
        return True
    
    def mock_get(key):
        return data_store.get(key)
    
    def mock_delete(key):
        if key in data_store:
            del data_store[key]
            return 1
        return 0
    
    def mock_exists(key):
        return 1 if key in data_store else 0
    
    def mock_zremrangebyscore(key, min_score, max_score):
        if key not in sorted_sets:
            sorted_sets[key] = []
        sorted_sets[key] = [(v, s) for v, s in sorted_sets[key] if s > max_score]
        return len(sorted_sets[key])
    
    def mock_zcard(key):
        if key not in sorted_sets:
            return 0
        return len(sorted_sets[key])
    
    def mock_zadd(key, mapping):
        if key not in sorted_sets:
            sorted_sets[key] = []
        for value, score in mapping.items():
            sorted_sets[key].append((value, score))
        return len(mapping)
    
    def mock_expire(key, time):
        return True
    
    def mock_zrange(key, start, end, withscores=False):
        if key not in sorted_sets or not sorted_sets[key]:
            return []
        if withscores:
            return sorted_sets[key][start:end+1]
        return [v for v, s in sorted_sets[key][start:end+1]]
    
    def mock_pipeline():
        pipe = Mock()
        pipe.zremrangebyscore = Mock(return_value=pipe)
        pipe.zcard = Mock(return_value=pipe)
        pipe.zadd = Mock(return_value=pipe)
        pipe.expire = Mock(return_value=pipe)
        
        # 模拟 execute 返回结果
        def mock_execute():
            key = "rate_limit:test_user"
            if key not in sorted_sets:
                sorted_sets[key] = []
            current_count = len(sorted_sets[key])
            sorted_sets[key].append((str(time.time()), time.time()))
            return [None, current_count, None, None]
        
        pipe.execute = mock_execute
        return pipe
    
    client.setex = mock_setex
    client.get = mock_get
    client.delete = mock_delete
    client.exists = mock_exists
    client.zremrangebyscore = mock_zremrangebyscore
    client.zcard = mock_zcard
    client.zadd = mock_zadd
    client.expire = mock_expire
    client.zrange = mock_zrange
    client.pipeline = mock_pipeline
    
    return client
