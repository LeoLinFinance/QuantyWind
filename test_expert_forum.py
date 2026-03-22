"""
测试智者论坛功能
"""
import asyncio
import sys
sys.path.append('backend')

from services.expert_forum_service import ExpertForumService
from services.portfolio_service import PortfolioService

async def test_expert_forum():
    """测试智者论坛服务"""
    
    print("=" * 60)
    print("测试智者论坛功能")
    print("=" * 60)
    
    # 初始化服务
    expert_service = ExpertForumService()
    portfolio_service = PortfolioService()
    
    # 1. 测试投资组合服务
    print("\n1. 测试投资组合服务")
    print("-" * 60)
    
    # 添加测试持仓
    portfolio_service.add_holding('AAPL', 100, 150.0)
    portfolio_service.add_holding('TSLA', 50, 200.0)
    portfolio_service.add_holding('NVDA', 30, 400.0)
    
    portfolio = portfolio_service.get_portfolio()
    print(f"✅ 当前持仓: {len(portfolio['holdings'])} 只股票")
    for holding in portfolio['holdings']:
        print(f"   - {holding['symbol']}: {holding['shares']}股 @ ${holding['cost_basis']}")
    
    # 2. 测试新闻资讯获取
    print("\n2. 测试新闻资讯获取")
    print("-" * 60)
    
    try:
        news_result = await expert_service.fetch_news_summary()
        print(f"✅ 新闻资讯获取成功")
        print(f"   时间戳: {news_result['timestamp']}")
        print(f"   关注股票: {', '.join(news_result['stock_symbols'])}")
        print(f"   内容长度: {len(news_result['content'])} 字符")
        print(f"\n   内容预览:")
        print(f"   {news_result['content'][:200]}...")
    except Exception as e:
        print(f"❌ 新闻资讯获取失败: {e}")
    
    # 3. 测试专家配置
    print("\n3. 测试专家配置")
    print("-" * 60)
    
    configs = await expert_service.get_expert_configs()
    print(f"✅ 当前配置数量: {len(configs)}")
    
    # 保存测试配置
    test_config = {
        'id': 'test_expert',
        'name': '测试专家',
        'prompt': '这是一个测试提示词'
    }
    await expert_service.save_expert_config(test_config)
    print(f"✅ 测试配置已保存")
    
    # 4. 测试专家分析（使用简短的上下文避免长时间等待）
    print("\n4. 测试专家分析")
    print("-" * 60)
    
    try:
        context = "市场最近表现良好，科技股普遍上涨。"
        analysis_result = await expert_service.get_expert_analysis(
            expert_id='stock_analyst',
            expert_name='选股分析师',
            expert_prompt='你是一位资深选股分析师，请简要分析当前市场并推荐2-3只股票。',
            context=context
        )
        print(f"✅ 专家分析完成")
        print(f"   专家: {analysis_result['expert_name']}")
        print(f"   时间戳: {analysis_result['timestamp']}")
        print(f"   分析长度: {len(analysis_result['analysis'])} 字符")
        print(f"\n   分析预览:")
        print(f"   {analysis_result['analysis'][:200]}...")
    except Exception as e:
        print(f"❌ 专家分析失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_expert_forum())
