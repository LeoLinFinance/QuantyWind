"""
投资组合服务
管理用户的股票持仓信息
"""
import logging
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class PortfolioService:
    """投资组合服务"""
    
    def __init__(self):
        self.portfolio_file = Path("data/portfolio.json")
        self.portfolio_file.parent.mkdir(exist_ok=True)
        
        # 初始化默认投资组合
        if not self.portfolio_file.exists():
            default_portfolio = {
                'holdings': [],
                'cash': 100000.0,
                'last_updated': datetime.now().isoformat()
            }
            self.portfolio_file.write_text(json.dumps(default_portfolio, indent=2))
        
        logger.info("✅ Portfolio Service initialized")
    
    def get_portfolio(self) -> Dict:
        """
        获取投资组合
        
        Returns:
            投资组合字典
        """
        try:
            if self.portfolio_file.exists():
                content = self.portfolio_file.read_text()
                return json.loads(content)
            return {'holdings': [], 'cash': 100000.0}
        except Exception as e:
            logger.error(f"读取投资组合失败: {e}")
            return {'holdings': [], 'cash': 100000.0}
    
    def update_portfolio(self, portfolio: Dict):
        """
        更新投资组合
        
        Args:
            portfolio: 投资组合字典
        """
        try:
            portfolio['last_updated'] = datetime.now().isoformat()
            self.portfolio_file.write_text(json.dumps(portfolio, ensure_ascii=False, indent=2))
            logger.info("✅ 投资组合已更新")
        except Exception as e:
            logger.error(f"更新投资组合失败: {e}")
            raise
    
    def add_holding(self, symbol: str, shares: float, cost_basis: float):
        """
        添加持仓
        
        Args:
            symbol: 股票代码
            shares: 股数
            cost_basis: 成本价
        """
        portfolio = self.get_portfolio()
        
        # 检查是否已存在
        for holding in portfolio['holdings']:
            if holding['symbol'] == symbol:
                # 更新现有持仓
                total_shares = holding['shares'] + shares
                total_cost = holding['shares'] * holding['cost_basis'] + shares * cost_basis
                holding['shares'] = total_shares
                holding['cost_basis'] = total_cost / total_shares
                self.update_portfolio(portfolio)
                return
        
        # 添加新持仓
        portfolio['holdings'].append({
            'symbol': symbol,
            'shares': shares,
            'cost_basis': cost_basis,
            'added_date': datetime.now().isoformat()
        })
        
        self.update_portfolio(portfolio)
    
    def remove_holding(self, symbol: str, shares: float = None):
        """
        移除持仓
        
        Args:
            symbol: 股票代码
            shares: 要移除的股数（None表示全部移除）
        """
        portfolio = self.get_portfolio()
        
        for i, holding in enumerate(portfolio['holdings']):
            if holding['symbol'] == symbol:
                if shares is None or shares >= holding['shares']:
                    # 完全移除
                    portfolio['holdings'].pop(i)
                else:
                    # 部分移除
                    holding['shares'] -= shares
                
                self.update_portfolio(portfolio)
                return
        
        logger.warning(f"未找到持仓: {symbol}")
    
    def get_holdings_symbols(self) -> List[str]:
        """
        获取所有持仓的股票代码
        
        Returns:
            股票代码列表
        """
        portfolio = self.get_portfolio()
        return [h['symbol'] for h in portfolio.get('holdings', [])]

