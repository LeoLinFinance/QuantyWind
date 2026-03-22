from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from routers import market, risk, sentiment, historical_data, ai_signals, persistence, expert_forum, api_keys
from services.scheduler import start_scheduler

# 导入安全中间件
from middleware.security_middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    HTTPSRedirectMiddleware,
    IPWhitelistMiddleware
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
ENABLE_HTTPS_REDIRECT = os.getenv("ENABLE_HTTPS_REDIRECT", "false").lower() == "true"
ENABLE_IP_WHITELIST = os.getenv("ENABLE_IP_WHITELIST", "false").lower() == "true"
IP_WHITELIST = set(os.getenv("IP_WHITELIST", "").split(",")) if os.getenv("IP_WHITELIST") else set()

app = FastAPI(
    title="量数风行 - 美股舆情风险分析平台",
    description="安全的远程访问部署系统",
    version="1.0.0",
    docs_url="/api/docs" if ENVIRONMENT == "development" else None,  # 生产环境禁用文档
    redoc_url="/api/redoc" if ENVIRONMENT == "development" else None
)

# ============================================================================
# 中间件配置
# 
# 执行顺序（从外到内）：
# 1. SecurityHeadersMiddleware - 添加安全头部
# 2. HTTPSRedirectMiddleware - 强制 HTTPS（生产环境）
# 3. RequestLoggingMiddleware - 请求日志记录
# 4. IPWhitelistMiddleware - IP 白名单控制（可选）
# 5. CORSMiddleware - CORS 处理
# 6. 应用路由处理
# 
# 注意：中间件按添加顺序的相反顺序执行（后添加的先执行）
# ============================================================================

# 1. 安全头部中间件（最外层，确保所有响应都有安全头部）
app.add_middleware(
    SecurityHeadersMiddleware,
    hsts_max_age=31536000,  # 1 年
    csp_policy=(
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
)

# 2. HTTPS 强制重定向（生产环境启用）
if ENABLE_HTTPS_REDIRECT:
    app.add_middleware(
        HTTPSRedirectMiddleware,
        enabled=True,
        exclude_paths={"/health", "/"}
    )
    logger.info("HTTPS redirect middleware enabled")

# 3. 请求日志记录中间件
app.add_middleware(
    RequestLoggingMiddleware,
    log_request_body=False,  # 不记录请求体（可能包含敏感信息）
    log_response_body=False,  # 不记录响应体（可能很大）
    exclude_paths={"/health", "/metrics"}
)

# 4. IP 白名单中间件（可选，用于保护管理端点）
if ENABLE_IP_WHITELIST and IP_WHITELIST:
    app.add_middleware(
        IPWhitelistMiddleware,
        whitelist=IP_WHITELIST,
        protected_paths={"/api/admin", "/api/audit"},
        enabled=True
    )
    logger.info(f"IP whitelist middleware enabled with {len(IP_WHITELIST)} IPs")

# 5. CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 从环境变量读取允许的源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # 预检请求缓存时间
)

# 注册路由
app.include_router(market.router, prefix="/api", tags=["market"])
app.include_router(risk.router, prefix="/api", tags=["risk"])
app.include_router(sentiment.router, prefix="/api", tags=["sentiment"])
app.include_router(historical_data.router, prefix="/api", tags=["historical_data"])
app.include_router(ai_signals.router, tags=["ai_signals"])
app.include_router(persistence.router, tags=["persistence"])
app.include_router(expert_forum.router, tags=["expert_forum"])
app.include_router(api_keys.router, tags=["api_keys"])

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    start_scheduler()
    logger.info("=" * 60)
    logger.info("量数风行 - 美股舆情风险分析平台启动")
    logger.info("=" * 60)
    logger.info(f"环境: {ENVIRONMENT}")
    logger.info(f"允许的 CORS 源: {ALLOWED_ORIGINS}")
    logger.info(f"HTTPS 重定向: {'启用' if ENABLE_HTTPS_REDIRECT else '禁用'}")
    logger.info(f"IP 白名单: {'启用' if ENABLE_IP_WHITELIST else '禁用'}")
    logger.info("中间件执行顺序:")
    logger.info("  1. SecurityHeadersMiddleware - 安全头部")
    logger.info("  2. HTTPSRedirectMiddleware - HTTPS 重定向")
    logger.info("  3. RequestLoggingMiddleware - 请求日志")
    logger.info("  4. IPWhitelistMiddleware - IP 白名单")
    logger.info("  5. CORSMiddleware - CORS 处理")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("应用关闭 - 清理资源")

@app.get("/")
async def root():
    return {
        "message": "量数风行 - 美股舆情风险分析平台 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """
    健康检查端点
    
    返回系统健康状态和配置信息
    用于监控系统和负载均衡器健康检查
    
    需求：11.3
    """
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "middleware": {
            "security_headers": True,
            "https_redirect": ENABLE_HTTPS_REDIRECT,
            "request_logging": True,
            "ip_whitelist": ENABLE_IP_WHITELIST,
            "cors": True
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=ENVIRONMENT == "development"
    )
