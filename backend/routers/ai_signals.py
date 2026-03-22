"""
AI智能交易信号分析 API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from services.ai_signals_service import AISignalsService, InsufficientDataError

router = APIRouter(prefix="/api/ai-signals", tags=["AI Signals"])
logger = logging.getLogger('ai_signals_router')

# 初始化服务
ai_signals_service = AISignalsService()


# ============================================================================
# 请求/响应模型
# ============================================================================

class PortfolioItem(BaseModel):
    symbol: str
    weight: float
    shares: Optional[int] = None
    cost_basis: Optional[float] = None


class PortfolioOptimizationRequest(BaseModel):
    portfolio: List[PortfolioItem]


class MarketTrendRequest(BaseModel):
    symbols: List[str]
    indices: Optional[List[str]] = None


class RiskMonitorRequest(BaseModel):
    portfolio: List[PortfolioItem]
    thresholds: Optional[Dict[str, float]] = None


# ============================================================================
# API端点
# ============================================================================

@router.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    """
    个股智能分析
    
    Args:
        symbol: 股票代码
    
    Returns:
        分析结果
    """
    try:
        result = ai_signals_service.analyze_stock(symbol)
        return result
    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}")
        raise HTTPException(status_code=500, detail="分析失败，请稍后重试")



@router.get("/trading-signal/{symbol}")
async def get_trading_signal(symbol: str):
    """
    获取交易信号
    
    Args:
        symbol: 股票代码
    
    Returns:
        交易信号
    """
    try:
        result = ai_signals_service.generate_trading_signal(symbol)
        return result
    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating trading signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="信号生成失败，请稍后重试")


@router.post("/optimize-portfolio")
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    """
    投资组合优化
    
    Args:
        request: 投资组合配置
    
    Returns:
        优化建议
    """
    try:
        portfolio = [item.dict() for item in request.portfolio]
        result = ai_signals_service.optimize_portfolio(portfolio)
        return result
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=500, detail="组合优化失败，请稍后重试")


@router.post("/market-trend")
async def predict_market_trend(request: MarketTrendRequest):
    """
    市场趋势预测
    
    Args:
        request: 关注的股票和指数列表
    
    Returns:
        趋势预测
    """
    try:
        result = ai_signals_service.predict_market_trend(
            symbols=request.symbols,
            indices=request.indices
        )
        return result
    except Exception as e:
        logger.error(f"Error predicting market trend: {e}")
        raise HTTPException(status_code=500, detail="趋势预测失败，请稍后重试")


@router.post("/risk-monitor")
async def monitor_risks(request: RiskMonitorRequest):
    """
    风险监控
    
    Args:
        request: 投资组合和风险阈值
    
    Returns:
        风险预警
    """
    try:
        portfolio = [item.dict() for item in request.portfolio]
        result = ai_signals_service.monitor_risks(
            portfolio=portfolio,
            thresholds=request.thresholds
        )
        return result
    except Exception as e:
        logger.error(f"Error monitoring risks: {e}")
        raise HTTPException(status_code=500, detail="风险监控失败，请稍后重试")



# ============================================================================
# 提示词管理
# ============================================================================

class CustomPromptRequest(BaseModel):
    prompt_type: str  # 'stock_analysis' 或 'trading_signal'
    prompt: str


@router.get("/prompts")
async def get_custom_prompts():
    """
    获取所有自定义提示词
    
    Returns:
        自定义提示词字典
    """
    try:
        prompts = ai_signals_service.custom_prompts
        return {
            'success': True,
            'prompts': prompts
        }
    except Exception as e:
        logger.error(f"Error getting custom prompts: {e}")
        raise HTTPException(status_code=500, detail="获取提示词失败")


@router.get("/prompts/{prompt_type}")
async def get_custom_prompt(prompt_type: str):
    """
    获取指定类型的自定义提示词
    
    Args:
        prompt_type: 提示词类型 ('stock_analysis' 或 'trading_signal')
    
    Returns:
        提示词内容
    """
    try:
        prompt = ai_signals_service.get_custom_prompt(prompt_type)
        return {
            'success': True,
            'prompt_type': prompt_type,
            'prompt': prompt,
            'is_custom': prompt is not None
        }
    except Exception as e:
        logger.error(f"Error getting custom prompt: {e}")
        raise HTTPException(status_code=500, detail="获取提示词失败")


@router.post("/prompts")
async def set_custom_prompt(request: CustomPromptRequest):
    """
    设置自定义提示词
    
    Args:
        request: 提示词请求
    
    Returns:
        操作结果
    """
    try:
        ai_signals_service.set_custom_prompt(request.prompt_type, request.prompt)
        return {
            'success': True,
            'message': f'{request.prompt_type} 提示词已保存',
            'prompt_type': request.prompt_type
        }
    except Exception as e:
        logger.error(f"Error setting custom prompt: {e}")
        raise HTTPException(status_code=500, detail="保存提示词失败")


@router.delete("/prompts/{prompt_type}")
async def delete_custom_prompt(prompt_type: str):
    """
    删除自定义提示词（恢复默认）
    
    Args:
        prompt_type: 提示词类型
    
    Returns:
        操作结果
    """
    try:
        if prompt_type in ai_signals_service.custom_prompts:
            del ai_signals_service.custom_prompts[prompt_type]
            ai_signals_service._save_custom_prompts()
            return {
                'success': True,
                'message': f'{prompt_type} 提示词已恢复默认'
            }
        else:
            return {
                'success': False,
                'message': f'{prompt_type} 没有自定义提示词'
            }
    except Exception as e:
        logger.error(f"Error deleting custom prompt: {e}")
        raise HTTPException(status_code=500, detail="删除提示词失败")
