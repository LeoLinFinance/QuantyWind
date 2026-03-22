"""
数据库配置模块
提供 PostgreSQL 和 Redis 连接配置
"""
import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# PostgreSQL 配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://quantflow_user:password@localhost:5432/quantflow"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_recycle=3600,   # 1小时后回收连接
    echo=False           # 生产环境关闭 SQL 日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# Redis 配置
REDIS_URL = os.getenv("REDIS_URL", "redis://:password@localhost:6379/0")

# 创建 Redis 客户端
redis_client: Optional[Redis] = None

def get_redis_client() -> Redis:
    """获取 Redis 客户端实例"""
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
    return redis_client

def get_db():
    """
    获取数据库会话
    用于 FastAPI 依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化数据库
    创建所有表（如果不存在）
    """
    Base.metadata.create_all(bind=engine)

def close_db_connections():
    """
    关闭所有数据库连接
    用于应用关闭时清理资源
    """
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None
    engine.dispose()
