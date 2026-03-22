"""
安全中间件模块

提供 HTTPS 强制重定向、安全头部和请求日志记录功能：
- HTTPS 强制重定向中间件
- 安全头部中间件（HSTS, CSP, X-Frame-Options）
- 请求日志记录中间件
- IP 地址控制中间件

需求：5.1, 5.5
"""

import time
import logging
from typing import Callable, Optional, Set
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.audit_log_service import AuditLogService
from database.config import get_db


# 配置日志
logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    HTTPS 强制重定向中间件
    
    将所有 HTTP 请求重定向到 HTTPS
    在生产环境中，通常由 Nginx 处理，这里作为备份
    
    需求：5.1
    """
    
    def __init__(
        self,
        app: ASGIApp,
        enabled: bool = True,
        exclude_paths: Optional[Set[str]] = None
    ):
        """
        初始化 HTTPS 重定向中间件
        
        Args:
            app: ASGI 应用
            enabled: 是否启用重定向（开发环境可能需要禁用）
            exclude_paths: 排除的路径集合（如健康检查端点）
        """
        super().__init__(app)
        self.enabled = enabled
        self.exclude_paths = exclude_paths or {"/health", "/"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 如果未启用或路径在排除列表中，直接放行
        if not self.enabled or request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # 检查是否使用 HTTPS
        # 注意：在反向代理后面时，需要检查 X-Forwarded-Proto 头部
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
        is_secure = (
            request.url.scheme == "https" or
            forwarded_proto == "https"
        )
        
        if not is_secure:
            # 构建 HTTPS URL
            https_url = request.url.replace(scheme="https")
            
            # 返回 301 永久重定向
            return Response(
                status_code=status.HTTP_301_MOVED_PERMANENTLY,
                headers={"Location": str(https_url)}
            )
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全头部中间件
    
    为所有响应添加安全相关的 HTTP 头部：
    - Strict-Transport-Security (HSTS)
    - Content-Security-Policy (CSP)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    
    需求：5.1, 5.5
    """
    
    def __init__(
        self,
        app: ASGIApp,
        hsts_max_age: int = 31536000,  # 1 年
        csp_policy: Optional[str] = None
    ):
        """
        初始化安全头部中间件
        
        Args:
            app: ASGI 应用
            hsts_max_age: HSTS 最大年龄（秒）
            csp_policy: 自定义 CSP 策略
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        
        # 默认 CSP 策略：严格但实用
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并添加安全头部"""
        response = await call_next(request)
        
        # HSTS - 强制使用 HTTPS
        response.headers["Strict-Transport-Security"] = (
            f"max-age={self.hsts_max_age}; includeSubDomains; preload"
        )
        
        # CSP - 内容安全策略
        response.headers["Content-Security-Policy"] = self.csp_policy
        
        # 防止 MIME 类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 防止点击劫持
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # XSS 保护（虽然现代浏览器已弃用，但仍添加以兼容旧浏览器）
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer 策略
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 权限策略 - 禁用不需要的浏览器功能
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志记录中间件
    
    记录所有 HTTP 请求的详细信息：
    - 请求方法、路径、查询参数
    - 客户端 IP 地址和 User-Agent
    - 响应状态码和处理时间
    - 错误和异常
    
    需求：7.1, 7.2
    """
    
    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: Optional[Set[str]] = None
    ):
        """
        初始化请求日志中间件
        
        Args:
            app: ASGI 应用
            log_request_body: 是否记录请求体（敏感数据需谨慎）
            log_response_body: 是否记录响应体（可能很大）
            exclude_paths: 排除的路径集合（如健康检查）
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or {"/health", "/metrics"}
    
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实 IP 地址
        
        考虑反向代理的情况，按优先级检查：
        1. X-Forwarded-For（可能包含多个 IP，取第一个）
        2. X-Real-IP
        3. request.client.host
        """
        # X-Forwarded-For 可能包含多个 IP，格式：client, proxy1, proxy2
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 直接连接的客户端 IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志"""
        # 如果路径在排除列表中，直接放行
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 提取请求信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        
        # 记录请求开始
        logger.info(
            f"Request started: {method} {path} "
            f"from {client_ip} ({user_agent})"
        )
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加处理时间头部
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # 记录请求完成
            logger.info(
                f"Request completed: {method} {path} "
                f"status={response.status_code} "
                f"time={process_time:.4f}s "
                f"ip={client_ip}"
            )
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录错误
            logger.error(
                f"Request failed: {method} {path} "
                f"error={str(e)} "
                f"time={process_time:.4f}s "
                f"ip={client_ip}",
                exc_info=True
            )
            
            # 重新抛出异常，让 FastAPI 的异常处理器处理
            raise


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    IP 白名单中间件
    
    限制只有白名单中的 IP 地址才能访问特定端点
    适用于管理端点或内部 API
    
    需求：9.1
    """
    
    def __init__(
        self,
        app: ASGIApp,
        whitelist: Optional[Set[str]] = None,
        protected_paths: Optional[Set[str]] = None,
        enabled: bool = False
    ):
        """
        初始化 IP 白名单中间件
        
        Args:
            app: ASGI 应用
            whitelist: 允许的 IP 地址集合
            protected_paths: 受保护的路径前缀集合
            enabled: 是否启用（默认禁用，需要明确配置）
        """
        super().__init__(app)
        self.whitelist = whitelist or set()
        self.protected_paths = protected_paths or {"/api/admin", "/api/audit"}
        self.enabled = enabled
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实 IP 地址"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_protected_path(self, path: str) -> bool:
        """检查路径是否受保护"""
        return any(path.startswith(prefix) for prefix in self.protected_paths)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并检查 IP 白名单"""
        # 如果未启用或路径不受保护，直接放行
        if not self.enabled or not self._is_protected_path(request.url.path):
            return await call_next(request)
        
        # 获取客户端 IP
        client_ip = self._get_client_ip(request)
        
        # 检查 IP 是否在白名单中
        if client_ip not in self.whitelist:
            logger.warning(
                f"IP whitelist violation: {client_ip} attempted to access "
                f"{request.url.path}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="访问被拒绝：您的 IP 地址不在允许列表中"
            )
        
        return await call_next(request)


# 便捷函数：创建配置好的中间件实例

def create_https_redirect_middleware(
    enabled: bool = True,
    exclude_paths: Optional[Set[str]] = None
) -> type:
    """
    创建 HTTPS 重定向中间件
    
    Args:
        enabled: 是否启用
        exclude_paths: 排除的路径
    
    Returns:
        配置好的中间件类
    """
    class ConfiguredHTTPSRedirectMiddleware(HTTPSRedirectMiddleware):
        def __init__(self, app: ASGIApp):
            super().__init__(app, enabled=enabled, exclude_paths=exclude_paths)
    
    return ConfiguredHTTPSRedirectMiddleware


def create_security_headers_middleware(
    hsts_max_age: int = 31536000,
    csp_policy: Optional[str] = None
) -> type:
    """
    创建安全头部中间件
    
    Args:
        hsts_max_age: HSTS 最大年龄
        csp_policy: CSP 策略
    
    Returns:
        配置好的中间件类
    """
    class ConfiguredSecurityHeadersMiddleware(SecurityHeadersMiddleware):
        def __init__(self, app: ASGIApp):
            super().__init__(app, hsts_max_age=hsts_max_age, csp_policy=csp_policy)
    
    return ConfiguredSecurityHeadersMiddleware


def create_request_logging_middleware(
    log_request_body: bool = False,
    log_response_body: bool = False,
    exclude_paths: Optional[Set[str]] = None
) -> type:
    """
    创建请求日志中间件
    
    Args:
        log_request_body: 是否记录请求体
        log_response_body: 是否记录响应体
        exclude_paths: 排除的路径
    
    Returns:
        配置好的中间件类
    """
    class ConfiguredRequestLoggingMiddleware(RequestLoggingMiddleware):
        def __init__(self, app: ASGIApp):
            super().__init__(
                app,
                log_request_body=log_request_body,
                log_response_body=log_response_body,
                exclude_paths=exclude_paths
            )
    
    return ConfiguredRequestLoggingMiddleware


def create_ip_whitelist_middleware(
    whitelist: Optional[Set[str]] = None,
    protected_paths: Optional[Set[str]] = None,
    enabled: bool = False
) -> type:
    """
    创建 IP 白名单中间件
    
    Args:
        whitelist: IP 白名单
        protected_paths: 受保护的路径
        enabled: 是否启用
    
    Returns:
        配置好的中间件类
    """
    class ConfiguredIPWhitelistMiddleware(IPWhitelistMiddleware):
        def __init__(self, app: ASGIApp):
            super().__init__(
                app,
                whitelist=whitelist,
                protected_paths=protected_paths,
                enabled=enabled
            )
    
    return ConfiguredIPWhitelistMiddleware
