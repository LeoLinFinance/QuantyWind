"""
认证中间件模块

提供 JWT 令牌验证、权限检查和请求限流功能：
- JWT 令牌验证中间件
- 权限检查装饰器
- 请求限流中间件（每用户每分钟 100 请求）

需求：2.1, 6.3
"""

import time
from functools import wraps
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from services.authentication_service import (
    get_authentication_service,
    AuthenticationService,
    TokenExpiredError,
    InvalidTokenError,
    TokenPayload
)
from services.authorization_service import AuthorizationService
from database.config import get_db, get_redis_client


# HTTP Bearer 认证方案
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """认证错误"""
    def __init__(self, detail: str = "未授权访问"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionDeniedError(HTTPException):
    """权限不足错误"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class RateLimitExceededError(HTTPException):
    """请求限流错误"""
    def __init__(self, detail: str = "请求过于频繁，请稍后再试"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"}
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_authentication_service)
) -> TokenPayload:
    """
    获取当前认证用户
    
    从请求头中提取 JWT 令牌并验证，返回令牌载荷
    
    Args:
        credentials: HTTP Bearer 认证凭证
        auth_service: 认证服务实例
    
    Returns:
        TokenPayload: 令牌载荷（包含用户信息）
    
    Raises:
        AuthenticationError: 认证失败
    """
    token = credentials.credentials
    
    try:
        # 验证令牌
        payload = auth_service.verify_token(token)
        return payload
    except TokenExpiredError:
        raise AuthenticationError(detail="令牌已过期，请重新登录")
    except InvalidTokenError as e:
        raise AuthenticationError(detail=f"令牌无效: {str(e)}")
    except Exception as e:
        raise AuthenticationError(detail=f"认证失败: {str(e)}")


def require_auth(func: Callable) -> Callable:
    """
    JWT 令牌验证装饰器
    
    要求请求必须包含有效的 JWT 令牌
    
    使用示例:
        @router.get("/protected")
        @require_auth
        async def protected_route(current_user: TokenPayload = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    
    Args:
        func: 要保护的路由函数
    
    Returns:
        Callable: 包装后的函数
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 检查是否有 current_user 参数
        if 'current_user' not in kwargs:
            raise AuthenticationError(detail="缺少认证信息")
        
        current_user = kwargs['current_user']
        if not isinstance(current_user, TokenPayload):
            raise AuthenticationError(detail="无效的认证信息")
        
        return await func(*args, **kwargs)
    
    return wrapper



def require_permission(resource: str, action: str) -> Callable:
    """
    权限检查装饰器
    
    检查当前用户是否有权限访问指定资源
    
    使用示例:
        @router.delete("/portfolio/{id}")
        @require_permission("portfolio", "delete")
        async def delete_portfolio(
            id: str,
            current_user: TokenPayload = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            # 删除投资组合
            pass
    
    Args:
        resource: 资源标识符（如 "portfolio", "market_data"）
        action: 操作类型（如 "read", "write", "delete"）
    
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前用户
            current_user = kwargs.get('current_user')
            if not current_user or not isinstance(current_user, TokenPayload):
                raise AuthenticationError(detail="缺少认证信息")
            
            # 获取数据库会话
            db = kwargs.get('db')
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库会话不可用"
                )
            
            # 检查权限
            auth_service = AuthorizationService(db)
            has_permission = auth_service.check_permission(
                user_id=current_user.user_id,
                resource=resource,
                action=action
            )
            
            if not has_permission:
                raise PermissionDeniedError(
                    detail=f"您没有权限执行此操作。需要 {resource}:{action} 权限"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class RateLimiter:
    """
    请求限流中间件
    
    实现基于用户的请求限流，防止滥用
    默认限制：每用户每分钟 100 请求
    
    使用示例:
        rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
        
        @router.get("/api/data")
        async def get_data(
            request: Request,
            current_user: TokenPayload = Depends(get_current_user)
        ):
            # 在路由处理器中调用
            rate_limiter.check_rate_limit(current_user.user_id)
            return {"data": "..."}
    """
    
    # Redis 键前缀
    REDIS_KEY_PREFIX = "rate_limit:"
    
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        redis_client=None
    ):
        """
        初始化限流器
        
        Args:
            max_requests: 时间窗口内允许的最大请求数
            window_seconds: 时间窗口大小（秒）
            redis_client: Redis 客户端实例（可选）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis = redis_client or get_redis_client()
    
    def _get_rate_limit_key(self, user_id: str) -> str:
        """获取限流的 Redis 键"""
        return f"{self.REDIS_KEY_PREFIX}{user_id}"
    
    def check_rate_limit(self, user_id: str) -> None:
        """
        检查用户是否超过请求限制
        
        使用滑动窗口算法实现限流：
        1. 使用 Redis 的 sorted set 存储请求时间戳
        2. 移除窗口外的旧请求
        3. 检查当前窗口内的请求数
        
        Args:
            user_id: 用户 ID
        
        Raises:
            RateLimitExceededError: 超过请求限制
        """
        key = self._get_rate_limit_key(user_id)
        now = time.time()
        window_start = now - self.window_seconds
        
        # 使用 Redis pipeline 提高性能
        pipe = self.redis.pipeline()
        
        # 移除窗口外的旧请求
        pipe.zremrangebyscore(key, 0, window_start)
        
        # 获取当前窗口内的请求数
        pipe.zcard(key)
        
        # 添加当前请求
        pipe.zadd(key, {str(now): now})
        
        # 设置键的过期时间（窗口大小 + 1 秒）
        pipe.expire(key, self.window_seconds + 1)
        
        # 执行 pipeline
        results = pipe.execute()
        
        # 获取当前窗口内的请求数（在添加当前请求之前）
        current_requests = results[1]
        
        # 检查是否超过限制
        if current_requests >= self.max_requests:
            raise RateLimitExceededError(
                detail=f"请求过于频繁。限制：{self.max_requests} 请求/{self.window_seconds} 秒"
            )
    
    def get_remaining_requests(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户剩余的请求配额
        
        Args:
            user_id: 用户 ID
        
        Returns:
            Dict[str, Any]: 包含剩余请求数和重置时间的字典
        """
        key = self._get_rate_limit_key(user_id)
        now = time.time()
        window_start = now - self.window_seconds
        
        # 移除窗口外的旧请求
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # 获取当前窗口内的请求数
        current_requests = self.redis.zcard(key)
        
        # 计算剩余请求数
        remaining = max(0, self.max_requests - current_requests)
        
        # 获取最早的请求时间戳
        oldest_requests = self.redis.zrange(key, 0, 0, withscores=True)
        
        if oldest_requests:
            oldest_timestamp = oldest_requests[0][1]
            reset_time = oldest_timestamp + self.window_seconds
        else:
            reset_time = now + self.window_seconds
        
        return {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset": int(reset_time),
            "reset_datetime": datetime.fromtimestamp(reset_time).isoformat()
        }
    
    def reset_rate_limit(self, user_id: str) -> bool:
        """
        重置用户的请求限制（管理员功能）
        
        Args:
            user_id: 用户 ID
        
        Returns:
            bool: 重置是否成功
        """
        key = self._get_rate_limit_key(user_id)
        return self.redis.delete(key) > 0


# 创建全局限流器实例
# 默认配置：每用户每分钟 100 请求
default_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


def apply_rate_limit(
    current_user: TokenPayload = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(lambda: default_rate_limiter)
) -> None:
    """
    应用请求限流的依赖项
    
    在路由中使用此依赖项来自动应用限流
    
    使用示例:
        @router.get("/api/data")
        async def get_data(
            current_user: TokenPayload = Depends(get_current_user),
            _: None = Depends(apply_rate_limit)
        ):
            return {"data": "..."}
    
    Args:
        current_user: 当前用户
        rate_limiter: 限流器实例
    
    Raises:
        RateLimitExceededError: 超过请求限制
    """
    rate_limiter.check_rate_limit(current_user.user_id)


# 便捷函数：创建自定义限流器依赖项
def create_rate_limiter(max_requests: int, window_seconds: int) -> Callable:
    """
    创建自定义限流器依赖项
    
    使用示例:
        # 创建更严格的限流器：每分钟 10 请求
        strict_rate_limit = create_rate_limiter(max_requests=10, window_seconds=60)
        
        @router.post("/api/expensive-operation")
        async def expensive_operation(
            current_user: TokenPayload = Depends(get_current_user),
            _: None = Depends(strict_rate_limit)
        ):
            return {"result": "..."}
    
    Args:
        max_requests: 时间窗口内允许的最大请求数
        window_seconds: 时间窗口大小（秒）
    
    Returns:
        Callable: 限流依赖项函数
    """
    limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
    
    def rate_limit_dependency(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> None:
        limiter.check_rate_limit(current_user.user_id)
    
    return rate_limit_dependency
