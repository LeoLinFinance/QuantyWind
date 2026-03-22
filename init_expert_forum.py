"""
初始化智者论坛测试数据
"""
import sys
sys.path.append('backend')

from services.portfolio_service import PortfolioService

def init_test_portfolio():
    """初始化测试投资组合"""
    
    print("=" * 60)
    print("初始化智者论坛测试数据")
    print("=" * 60)
    
    portfolio_service = PortfolioService()
    
    # 添加测试持仓（美股和港股）
    test_holdings = [
        # 美股科技股
        ('AAPL', 100, 150.0, '苹果'),
        ('MSFT', 80, 300.0, '微软'),
        ('GOOGL', 40, 120.0, '谷歌'),
        ('NVDA', 30, 400.0, '英伟达'),
        ('TSLA', 50, 200.0, '特斯拉'),
        
        # 美股其他行业
        ('JPM', 60, 140.0, '摩根大通'),
        ('JNJ', 70, 160.0, '强生'),
        
        # 港股（使用.HK后缀）
        ('0700.HK', 200, 350.0, '腾讯'),
        ('9988.HK', 150, 80.0, '阿里巴巴'),
    ]
    
    print("\n添加测试持仓...")
    print("-" * 60)
    
    for symbol, shares, cost, name in test_holdings:
        portfolio_service.add_holding(symbol, shares, cost)
        print(f"✅ {name} ({symbol}): {shares}股 @ ${cost}")
    
    # 显示最终投资组合
    portfolio = portfolio_service.get_portfolio()
    
    print("\n" + "=" * 60)
    print("投资组合初始化完成")
    print("=" * 60)
    print(f"\n持仓数量: {len(portfolio['holdings'])} 只股票")
    print(f"现金余额: ${portfolio['cash']:,.2f}")
    
    total_value = sum(h['shares'] * h['cost_basis'] for h in portfolio['holdings'])
    print(f"持仓市值: ${total_value:,.2f}")
    print(f"总资产: ${portfolio['cash'] + total_value:,.2f}")
    
    print("\n持仓明细:")
    for holding in portfolio['holdings']:
        value = holding['shares'] * holding['cost_basis']
        print(f"  {holding['symbol']:10s} {holding['shares']:6.0f}股 @ ${holding['cost_basis']:7.2f} = ${value:10.2f}")
    
    print("\n" + "=" * 60)
    print("现在可以启动智者论坛进行测试")
    print("=" * 60)

if __name__ == "__main__":
    init_test_portfolio()
