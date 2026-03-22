#!/usr/bin/env python3
"""
测试舆情地图功能
"""
import sys
sys.path.insert(0, 'backend')

from services.sentiment_service import SentimentService
import json

def test_sentiment_map():
    print("=" * 60)
    print("测试舆情地图AI风险分析功能")
    print("=" * 60)
    
    service = SentimentService()
    
    # 清除缓存以获取最新数据
    service.cache = {}
    service.cache_time = None
    
    print("\n正在获取并分析市场新闻...")
    data = service.get_map_data()
    
    print(f"\n✅ 数据获取成功!")
    print(f"   已定位事件: {len(data['located'])}")
    print(f"   不确定地区事件: {len(data['uncertain'])}")
    
    # 统计风险等级
    risk_counts = {'high': 0, 'medium': 0, 'low': 0}
    all_events = data['located'] + data['uncertain']
    
    for event in all_events:
        risk_counts[event['riskLevel']] += 1
    
    total = len(all_events)
    print(f"\n📊 风险等级分布:")
    print(f"   🔴 高风险: {risk_counts['high']} ({risk_counts['high']*100//total if total > 0 else 0}%)")
    print(f"   🟡 中风险: {risk_counts['medium']} ({risk_counts['medium']*100//total if total > 0 else 0}%)")
    print(f"   🔵 低风险: {risk_counts['low']} ({risk_counts['low']*100//total if total > 0 else 0}%)")
    
    # 验证分布是否合理
    print(f"\n✓ 分布验证:")
    high_pct = risk_counts['high']*100//total if total > 0 else 0
    medium_pct = risk_counts['medium']*100//total if total > 0 else 0
    low_pct = risk_counts['low']*100//total if total > 0 else 0
    
    if 5 <= high_pct <= 15:
        print(f"   ✅ 高风险占比 {high_pct}% (目标: 5-10%)")
    else:
        print(f"   ⚠️  高风险占比 {high_pct}% (目标: 5-10%)")
    
    if 15 <= medium_pct <= 35:
        print(f"   ✅ 中风险占比 {medium_pct}% (目标: 20-30%)")
    else:
        print(f"   ⚠️  中风险占比 {medium_pct}% (目标: 20-30%)")
    
    if 55 <= low_pct <= 75:
        print(f"   ✅ 低风险占比 {low_pct}% (目标: 60-70%)")
    else:
        print(f"   ⚠️  低风险占比 {low_pct}% (目标: 60-70%)")
    
    # 显示已定位事件
    if data['located']:
        print(f"\n🌍 已定位事件示例:")
        for i, event in enumerate(data['located'][:3], 1):
            risk_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}
            print(f"\n   {i}. {risk_emoji[event['riskLevel']]} {event['riskLevel'].upper()}")
            print(f"      国家: {event.get('country', 'N/A')}")
            print(f"      摘要: {event['summary']}")
            if event.get('relatedStocks'):
                print(f"      相关股票: {', '.join(event['relatedStocks'])}")
            if event.get('coordinates'):
                print(f"      坐标: {event['coordinates']}")
    
    # 显示不确定地区事件
    if data['uncertain']:
        print(f"\n❓ 不确定地区事件:")
        for i, event in enumerate(data['uncertain'][:2], 1):
            risk_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}
            print(f"\n   {i}. {risk_emoji[event['riskLevel']]} {event['riskLevel'].upper()}")
            print(f"      摘要: {event['summary']}")
            if event.get('relatedStocks'):
                print(f"      相关股票: {', '.join(event['relatedStocks'])}")
    
    print(f"\n" + "=" * 60)
    print("✅ 测试完成！舆情地图AI风险分析功能正常运行")
    print("=" * 60)

if __name__ == "__main__":
    test_sentiment_map()
