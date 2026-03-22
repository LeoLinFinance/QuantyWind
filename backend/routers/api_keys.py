"""
API Key 管理路由
提供用户自定义 API Key 的管理接口
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging
from sqlalchemy.orm import Session

from services.api_key_service import APIKeyService
from database.config import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/api-keys", tags=["API Keys"])


class APIKeyCreate(BaseModel):
    """创建 API Key 请求"""
    provider: str  # stepfun, kimi, openai 等
    api_key: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[str] = None  # 为空表示系统默认


class APIKeyUpdate(BaseModel):
    """更新 API Key 请求"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/")
async def create_api_key(request: APIKeyCreate, db: Session = Depends(get_db)):
    """
    创建新的 API Key
    
    支持的 provider:
    - stepfun: 阶跃星辰
    - kimi: Kimi (月之暗面)
    - openai: OpenAI
    """
    try:
        service = APIKeyService(db)
        api_key = service.create_api_key(
            provider=request.provider,
            api_key=request.api_key,
            user_id=request.user_id,
            base_url=request.base_url,
            model=request.model,
            name=request.name,
            description=request.description
        )
        return api_key.to_dict(include_key=False)
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_api_keys(
    user_id: Optional[str] = None,
    provider: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取 API Keys 列表
    
    参数:
    - user_id: 用户ID（可选，为空获取系统默认配置）
    - provider: 过滤特定提供商（可选）
    """
    try:
        service = APIKeyService(db)
        api_keys = service.get_user_api_keys(user_id=user_id, provider=provider)
        return [key.to_dict(include_key=False) for key in api_keys]
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{key_id}")
async def get_api_key(key_id: str, db: Session = Depends(get_db)):
    """获取指定的 API Key（不包含完整密钥）"""
    try:
        service = APIKeyService(db)
        api_key = service.get_api_key(key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API Key not found")
        return api_key.to_dict(include_key=False)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{key_id}")
async def update_api_key(
    key_id: str,
    request: APIKeyUpdate,
    db: Session = Depends(get_db)
):
    """更新 API Key"""
    try:
        service = APIKeyService(db)
        api_key = service.update_api_key(
            key_id=key_id,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model,
            name=request.name,
            description=request.description,
            is_active=request.is_active
        )
        if not api_key:
            raise HTTPException(status_code=404, detail="API Key not found")
        return api_key.to_dict(include_key=False)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{key_id}")
async def delete_api_key(key_id: str, db: Session = Depends(get_db)):
    """删除 API Key"""
    try:
        service = APIKeyService(db)
        success = service.delete_api_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API Key not found")
        return {"message": "API Key deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/list")
async def list_providers():
    """获取支持的 AI 服务提供商列表"""
    return {
        "providers": [
            {
                "id": "stepfun",
                "name": "阶跃星辰 (StepFun)",
                "base_url": "https://api.stepfun.com/v1",
                "models": ["step-1-8k", "step-1-32k", "step-1-128k", "step-1-256k", "step-1v-8k"],
                "description": "国产大模型，支持长文本和视觉理解"
            },
            {
                "id": "kimi",
                "name": "Kimi (月之暗面)",
                "base_url": "https://api.moonshot.cn/v1",
                "models": ["kimi-k2-turbo-preview", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
                "description": "支持超长上下文和在线搜索"
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "base_url": "https://api.openai.com/v1",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "description": "OpenAI 官方模型"
            }
        ]
    }
