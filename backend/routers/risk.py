from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.risk_service import RiskService
from services.stepfun_service import StepFunService

router = APIRouter()
risk_service = RiskService()
stepfun_service = StepFunService()

class PortfolioItem(BaseModel):
    symbol: str
    weight: float
    name: str = ""  # 股票名称，可选

class PortfolioRequest(BaseModel):
    portfolio: List[PortfolioItem]

class RiskInterpretationRequest(BaseModel):
    portfolio: List[PortfolioItem]
    risk_metrics: dict

@router.get("/risk-models")
async def get_risk_models():
    """获取所有风险模型数据"""
    return risk_service.get_all_models()

@router.get("/risk-models/{model_name}")
async def get_risk_model(model_name: str):
    """获取特定风险模型详情"""
    return risk_service.get_model_detail(model_name)

@router.post("/portfolio-risk")
async def calculate_portfolio_risk(request: PortfolioRequest):
    """
    计算投资组合的风险指标
    
    请求体示例:
    {
        "portfolio": [
            {"symbol": "AAPL", "weight": 0.3},
            {"symbol": "MSFT", "weight": 0.3},
            {"symbol": "GOOGL", "weight": 0.4}
        ]
    }
    """
    try:
        portfolio = [item.dict() for item in request.portfolio]
        risk_metrics = risk_service.calculate_portfolio_risk(portfolio)
        return {
            'success': True,
            'portfolio': portfolio,
            'risk_metrics': risk_metrics
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")

@router.post("/portfolio-risk/interpret")
async def interpret_portfolio_risk(request: RiskInterpretationRequest):
    """
    使用AI解读投资组合风险指标
    
    请求体示例:
    {
        "portfolio": [
            {"symbol": "AAPL", "weight": 0.3, "name": "Apple Inc."},
            {"symbol": "MSFT", "weight": 0.3, "name": "Microsoft"},
            {"symbol": "GOOGL", "weight": 0.4, "name": "Alphabet"}
        ],
        "risk_metrics": {
            "var_95": -0.0234,
            "volatility": 0.18,
            ...
        }
    }
    """
    try:
        portfolio = [item.dict() for item in request.portfolio]
        interpretation = stepfun_service.interpret_portfolio_risk(
            portfolio=portfolio,
            risk_metrics=request.risk_metrics
        )
        return {
            'success': True,
            'interpretation': interpretation
        }
    except Exception as e:
        print(f"❌ AI解读失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI解读失败: {str(e)}")
