from fastapi import APIRouter, Query
from typing import Optional, List
from services.sentiment_service import SentimentService

router = APIRouter()
sentiment_service = SentimentService()

@router.get("/sentiment-map")
async def get_sentiment_map(custom_prompt: Optional[str] = Query(None)):
    """获取舆情地图数据"""
    return sentiment_service.get_map_data(custom_prompt)

@router.get("/sentiment-map/default-prompt")
async def get_default_prompt():
    """获取默认system prompt"""
    return {"prompt": sentiment_service.default_system_prompt}

@router.post("/industry-insights")
async def get_industry_insights(watchlist: List[str]):
    """获取产业链洞察"""
    return sentiment_service.get_industry_insights(watchlist)
