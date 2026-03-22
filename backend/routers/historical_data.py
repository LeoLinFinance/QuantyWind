"""
历史数据API路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from services.historical_data_service import HistoricalDataService

router = APIRouter()
historical_service = HistoricalDataService()

class UpdateRequest(BaseModel):
    watchlist_symbols: List[str]

@router.post("/historical-data/update")
async def update_historical_data(request: UpdateRequest):
    """
    更新历史数据（增量更新）
    只更新从上次更新到现在的数据
    """
    try:
        stats = historical_service.update_all_active_symbols(request.watchlist_symbols)
        return {
            'success': True,
            'stats': stats,
            'message': f"更新完成: {len(stats['updated'])}个成功, {len(stats['failed'])}个失败"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical-data/summary")
async def get_data_summary():
    """获取数据集摘要"""
    try:
        summary = historical_service.get_all_symbols_data()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical-data/statistics")
async def get_statistics():
    """获取数据集统计信息"""
    try:
        stats = historical_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical-data/{symbol}")
async def get_symbol_data(
    symbol: str,
    is_index: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取某个标的的历史数据"""
    try:
        data = historical_service.get_symbol_data(
            symbol, 
            is_index=is_index,
            start_date=start_date,
            end_date=end_date
        )
        return {
            'symbol': symbol,
            'data': data,
            'count': len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
