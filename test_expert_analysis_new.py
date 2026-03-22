"""
测试专家分析新输入格式
"""
import sys
sys.path.append('backend')

from services.expert_forum_service import ExpertForumService
import asyncio

async def test_expert_analysis():
    """测试专家分析功能"""
    
    print("=" * 60)
    print("测试专家分析新输入格式")
    print("=" * 60)
    
    # 初始化服务
    service = ExpertForumService()
    
    # 模拟最后一次资讯总结
    mock_news_summary = """[kimi] ### 市场总结报告

#### 1. 市场整体趋势和情绪
市场整体情绪较为积极，AI相关股票表现强劲，但部分个股面临挑战。

#### 2. 重要的宏观经济事件和数据
- AI投资热潮持续，推动相关股票上涨
- 美联储维持利率不变，市场预期年内降息

#### 3. 关键个股的重大新闻
- Apple (AAPL): 股价走弱，投资者重新评估增长前景
- NVIDIA (NVDA): 面临超大规模企业支出放缓风险
- Microsoft (MSFT): AI技术应用推动股价上涨

#### 4. 对投资组合的潜在影响
- 持仓中的AAPL可能需要关注短期压力
- MSFT和GOOGL受益于AI趋势，可考虑增持
- NVDA需要密切关注客户支出动态"""
    
    # 测试专家分析
    print("\n测试专家分析（使用最新资讯和实时价格）")
    print("-" * 60)
    
    expert_prompt = """你是一位资深市场分析师，专注于短期价格投资分析。
请根据最新市场资讯和当前持仓情况，分析是否需要做适当的减仓或清仓以规避短期风险。
请提供具体的技术指标分析和操作建议。"""
    
    try:
        result = await service.get_expert_analysis(
            expert_id='market_analyst',
            expert_name='市场分析师',
            expert_prompt=expert_prompt,
            context=mock_news_summary
        )
        
        print(f"✅ 专家分析成功")
        print(f"   专家: {result['expert_name']}")
        print(f"   分析股票数: {result.get('holdings_analyzed', 0)}")
        print(f"   时间戳: {result['timestamp']}")
        print(f"\n   分析内容:")
        print(f"   {result['analysis'][:500]}...")
        
    except Exception as e:
        print(f"❌ 专家分析失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_expert_analysis())
