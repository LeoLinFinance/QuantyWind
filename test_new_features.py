#!/usr/bin/env python3
"""
测试新增功能：
1. 地图标记详细信息（风险详情、受影响产业）
2. 产业链洞察
3. 自定义system prompt
"""
import sys
sys.path.insert(0, 'backend')

from services.sentiment_service import SentimentService

def test_detailed_risk_info():
    print("=" * 60)
    print("测试1: 风险事件详细信息")
    print("=" * 60)
    
    service = SentimentService()
    service.cache = {}
    service.cache_time = None
    
    print("\n正在获取舆情地图数据...")
    data = service.get_map_data()
    
    if data['located']:
        event = data['located'][0]
        print(f"\n✅ 事件详情示例:")
        print(f"   摘要: {event['summary']}")
        print(f"   风险等级: {event['riskLevel']}")
        print(f"   风险详情: {event.get('riskDetails', '无')[:100]}...")
        print(f"   受影响产业: {event.get('affectedIndustries', [])}")
        print(f"   相关股票: {event.get('relatedStocks', [])}")
        print(f"   国家: {event.get('country', '未确定')}")
    else:
        print("\n⚠️  暂无已定位事件")

def test_industry_insights():
    print("\n" + "=" * 60)
    print("测试2: 产业链洞察")
    print("=" * 60)
    
    service = SentimentService()
    watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL']
    
    print(f"\n正在分析盯盘股票的产业链动态...")
    print(f"盯盘股票: {', '.join(watchlist)}")
    
    insights = service.get_industry_insights(watchlist)
    
    print(f"\n✅ 获得 {len(insights)} 个产业链洞见:")
    for i, insight in enumerate(insights, 1):
        print(f"\n洞见 {i}:")
        print(f"   标题: {insight['title']}")
        print(f"   内容: {insight['content'][:100]}...")
        print(f"   情绪: {insight['sentiment']}")
        print(f"   相关股票: {', '.join(insight['related_stocks'])}")

def test_custom_prompt():
    print("\n" + "=" * 60)
    print("测试3: 自定义System Prompt")
    print("=" * 60)
    
    service = SentimentService()
    
    print(f"\n✅ 默认提示词长度: {len(service.default_system_prompt)} 字符")
    print(f"   提示词预览: {service.default_system_prompt[:100]}...")
    
    custom_prompt = "你是一个保守的风险分析师，倾向于将事件评估为更高风险。"
    print(f"\n✅ 自定义提示词: {custom_prompt}")
    print(f"   (实际使用时会影响AI的风险判断)")

if __name__ == "__main__":
    try:
        test_detailed_risk_info()
        test_industry_insights()
        test_custom_prompt()
        
        print("\n" + "=" * 60)
        print("✅ 所有新功能测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
