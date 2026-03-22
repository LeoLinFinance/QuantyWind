"""
测试阶跃星辰风险解读功能
"""
import sys
sys.path.append('backend')

from services.stepfun_service import StepFunService

def test_risk_interpretation():
    """测试风险解读功能"""
    
    # 创建服务实例
    service = StepFunService()
    
    # 模拟投资组合
    portfolio = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'weight': 0.3},
        {'symbol': 'MSFT', 'name': 'Microsoft', 'weight': 0.3},
        {'symbol': 'GOOGL', 'name': 'Alphabet', 'weight': 0.4}
    ]
    
    # 模拟风险指标
    risk_metrics = {
        'var_95': -0.0234,
        'var_99': -0.0312,
        'cvar_95': -0.0289,
        'volatility': 0.18,
        'sharpe_ratio': 1.25,
        'sortino_ratio': 1.45,
        'max_drawdown': -0.15,
        'beta': 1.08,
        'annual_return': 0.12,
        'skewness': -0.23,
        'kurtosis': 3.45,
        'correlation_matrix': {}
    }
    
    print("=" * 80)
    print("测试阶跃星辰风险解读功能")
    print("=" * 80)
    print("\n投资组合:")
    for item in portfolio:
        print(f"  - {item['symbol']} ({item['name']}): {item['weight']*100:.1f}%")
    
    print("\n风险指标:")
    print(f"  VaR (95%): {risk_metrics['var_95']*100:.2f}%")
    print(f"  年化波动率: {risk_metrics['volatility']*100:.2f}%")
    print(f"  夏普比率: {risk_metrics['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {risk_metrics['max_drawdown']*100:.2f}%")
    
    print("\n正在调用阶跃星辰API生成解读...")
    print("-" * 80)
    
    try:
        interpretation = service.interpret_portfolio_risk(portfolio, risk_metrics)
        print("\n✅ AI解读结果:")
        print("=" * 80)
        print(interpretation)
        print("=" * 80)
        print("\n✅ 测试成功！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_risk_interpretation()
