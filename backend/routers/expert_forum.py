"""
智者论坛路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from services.expert_forum_service import ExpertForumService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert-forum")

# 初始化服务
expert_forum_service = ExpertForumService()

class NewsRequest(BaseModel):
    last_time: Optional[str] = None

class ExpertAnalysisRequest(BaseModel):
    expert_id: str
    expert_name: str
    expert_prompt: str
    context: str
    model: Optional[str] = None  # 添加可选的模型参数

class ExpertConfig(BaseModel):
    id: str
    name: str
    prompt: str
    model: Optional[str] = None  # 添加可选的模型参数

@router.post("/news")
async def get_news_summary(request: NewsRequest):
    """
    获取KimiClaw的新闻资讯总结
    """
    try:
        result = await expert_forum_service.fetch_news_summary(request.last_time)
        return result
    except Exception as e:
        logger.error(f"获取新闻失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/news/stop")
async def stop_news():
    """
    通知KimiClaw停止推送
    """
    try:
        await expert_forum_service.stop_news_feed()
        return {"status": "stopped"}
    except Exception as e:
        logger.error(f"停止新闻推送失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expert-analysis")
async def get_expert_analysis(request: ExpertAnalysisRequest):
    """
    获取专家分析
    """
    try:
        result = await expert_forum_service.get_expert_analysis(
            expert_id=request.expert_id,
            expert_name=request.expert_name,
            expert_prompt=request.expert_prompt,
            context=request.context,
            model=request.model  # 传递模型参数
        )
        # 如果专家选择不回复，返回特殊标记
        if result is None:
            return {"skipped": True, "expert_name": request.expert_name}
        return result
    except Exception as e:
        logger.error(f"专家分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configs")
async def get_expert_configs():
    """
    获取专家配置
    """
    try:
        configs = await expert_forum_service.get_expert_configs()
        return configs
    except Exception as e:
        logger.error(f"获取专家配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configs")
async def save_expert_config(config: ExpertConfig):
    """
    保存专家配置
    """
    try:
        await expert_forum_service.save_expert_config(config.dict())
        return {"status": "saved"}
    except Exception as e:
        logger.error(f"保存专家配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary-prompt")
async def get_summary_prompt():
    """
    获取资讯总结提示词
    """
    try:
        prompt = await expert_forum_service.get_summary_prompt()
        return {"prompt": prompt}
    except Exception as e:
        logger.error(f"获取总结提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary-prompt")
async def save_summary_prompt(request: dict):
    """
    保存资讯总结提示词
    """
    try:
        prompt = request.get('prompt', '')
        if not prompt:
            raise HTTPException(status_code=400, detail="提示词不能为空")
        
        await expert_forum_service.save_summary_prompt(prompt)
        return {"status": "saved"}
    except Exception as e:
        logger.error(f"保存总结提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class UserMessageRequest(BaseModel):
    content: str

@router.post("/messages")
async def add_user_message(request: UserMessageRequest):
    """
    添加用户消息
    """
    try:
        message = await expert_forum_service.add_user_message(request.content)
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加用户消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages")
async def get_conversation_history():
    """
    获取对话历史
    """
    try:
        messages = await expert_forum_service.get_conversation_history()
        return {"messages": messages}
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/reset")
async def reset_conversation():
    """
    重置对话
    """
    try:
        await expert_forum_service.reset_conversation()
        return {"status": "reset"}
    except Exception as e:
        logger.error(f"重置对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-stats")
async def get_chat_stats():
    """
    获取聊天统计信息
    """
    try:
        stats = expert_forum_service.get_chat_stats()
        return stats
    except Exception as e:
        logger.error(f"获取聊天统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
