from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime
from services.market_service import MarketService
from pydantic import BaseModel

router = APIRouter()
market_service = MarketService()

class SystemPromptUpdate(BaseModel):
    prompt: str

@router.get("/market-insight")
async def get_market_insight(force_refresh: bool = Query(default=False)):
    """
    获取市场整体洞察
    
    Args:
        force_refresh: 是否强制刷新缓存（默认False，使用缓存）
    """
    return market_service.get_latest_insight(force_refresh=force_refresh)

@router.get("/watchlist")
async def get_watchlist(
    use_ai: bool = Query(default=True),
    force_refresh: bool = Query(default=False)
):
    """
    获取盯盘股票列表
    
    Args:
        use_ai: 是否使用AI分析舆情
        force_refresh: 是否强制刷新缓存（默认False，使用缓存）
    """
    return market_service.get_watchlist(use_ai=use_ai, force_refresh=force_refresh)

@router.get("/stock/{symbol}")
async def get_single_stock(symbol: str):
    """
    获取单只股票的数据（不含AI舆情）
    用于添加股票时只获取新股票的数据
    """
    stock = market_service.get_single_stock(symbol)
    if stock:
        return stock
    else:
        return {"error": "Stock not found"}

@router.get("/active-stocks")
async def get_active_stocks():
    """
    获取所有活跃股票列表（用于投资组合配置）
    只返回当前在盯盘列表中的股票
    """
    return market_service.get_watchlist(use_ai=False)

@router.post("/watchlist/{symbol}")
async def add_to_watchlist(symbol: str):
    """添加股票到盯盘列表"""
    return market_service.add_stock(symbol)

@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(symbol: str):
    """从盯盘列表移除股票"""
    return market_service.remove_stock(symbol)

@router.get("/search-stock")
async def search_stock(query: str = Query(..., min_length=1)):
    """搜索股票"""
    return market_service.search_stock(query)

@router.get("/system-prompt")
async def get_system_prompt():
    """获取当前系统提示词"""
    return market_service.get_system_prompt()

@router.post("/system-prompt")
async def update_system_prompt(data: SystemPromptUpdate):
    """更新系统提示词"""
    return market_service.update_system_prompt(data.prompt)
