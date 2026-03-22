"""
持久化数据管理 API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from services.persistence_service import PersistenceService

router = APIRouter(prefix="/api/persistence", tags=["Persistence"])
logger = logging.getLogger('persistence_router')

# 初始化服务
persistence_service = PersistenceService()


# ============================================================================
# API端点
# ============================================================================

@router.get("/info")
async def get_persistence_info():
    """
    获取所有持久化数据的信息
    
    Returns:
        数据信息
    """
    try:
        info = persistence_service.get_all_data_info()
        return {
            'success': True,
            'data': info
        }
    except Exception as e:
        logger.error(f"Error getting persistence info: {e}")
        raise HTTPException(status_code=500, detail="获取数据信息失败")


@router.get("/watchlist")
async def get_watchlist():
    """
    获取盯盘列表
    
    Returns:
        股票代码列表
    """
    try:
        symbols = persistence_service.load_watchlist()
        return {
            'success': True,
            'symbols': symbols,
            'count': len(symbols)
        }
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail="获取盯盘列表失败")


@router.get("/system-prompt")
async def get_system_prompt():
    """
    获取系统提示词
    
    Returns:
        提示词内容
    """
    try:
        prompt = persistence_service.load_system_prompt()
        return {
            'success': True,
            'prompt': prompt
        }
    except Exception as e:
        logger.error(f"Error getting system prompt: {e}")
        raise HTTPException(status_code=500, detail="获取系统提示词失败")


@router.get("/user-settings")
async def get_user_settings():
    """
    获取用户设置
    
    Returns:
        设置字典
    """
    try:
        settings = persistence_service.load_user_settings()
        return {
            'success': True,
            'settings': settings
        }
    except Exception as e:
        logger.error(f"Error getting user settings: {e}")
        raise HTTPException(status_code=500, detail="获取用户设置失败")


@router.delete("/clear-all")
async def clear_all_data():
    """
    清除所有持久化数据（慎用）
    
    Returns:
        操作结果
    """
    try:
        success = persistence_service.clear_all_data()
        if success:
            return {
                'success': True,
                'message': '所有持久化数据已清除'
            }
        else:
            raise HTTPException(status_code=500, detail="清除数据失败")
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail="清除数据失败")
