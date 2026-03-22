#!/usr/bin/env python3
"""
验证每个专家和服务的API Key分配
"""
import sys
from pathlib import Path

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("\n" + "="*70)
print("API Key分配验证")
print("="*70)

print("\n【目标】")
print("为每个专家和总结服务分配独立的API Key，避免并发调用超时")

# 验证1: 资讯总结服务
print("\n1. 资讯总结服务...")
try:
    from services.news_summary_service import NewsSummaryService
    service = NewsSummaryService()
    
    api_key = service.client.api_key
    print(f"   ✅ API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"   ✅ 用途: 新闻总结")
    
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 验证2: 对话总结服务
print("\n2. 对话总结服务（超过10条消息时）...")
try:
    from services.context_summarizer import ContextSummarizer
    service = ContextSummarizer()
    
    if service.client:
        api_key = service.client.api_key
        print(f"   ✅ API Key: {api_key[:20]}...{api_key[-10:]}")
        print(f"   ✅ 用途: 对话总结（与资讯总结共用）")
    else:
        print(f"   ⚠️  客户端未初始化")
    
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 验证3: 专家论坛服务
print("\n3. 专家论坛服务...")
try:
    from services.expert_forum_service import ExpertForumService
    service = ExpertForumService()
    
    print(f"   ✅ 专家API Key配置:")
    for expert_id, api_key in service.expert_api_keys.items():
        expert_names = {
            'stock_analyst': '选股分析师',
            'industry_analyst': '产业链分析师',
            'market_analyst': '市场分析师',
            'value_investor': '长期价值投资分析师',
            'chief_economist': '首席经济学家'
        }
        expert_name = expert_names.get(expert_id, expert_id)
        print(f"      - {expert_name:12s}: {api_key[:20]}...{api_key[-10:]}")
    
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 总结
print("\n" + "="*70)
print("API Key分配总结")
print("="*70)

print("\n【分配方案】")
print("1. 资讯总结 & 对话总结:")
print("   API Key: 4oZN16sWiAKwBEQvnb6nxr0mX31kJ1MsDqZBiuzly1UOPsXaDHgFKyo7QNSfvaC4")
print("   用途: 新闻总结 + 超过10条消息的对话总结")

print("\n2. 选股分析师:")
print("   API Key: 71l4il2y6OSbR76taoahpsCSfWepmQZpEUsLG2GYqpFOVK8LEV0PyynJ2MUp29q23")

print("\n3. 产业链分析师:")
print("   API Key: 2g1A2I9A51ec8iyzhiCqTYo94AHmt9fEXFb5L93WmZPFSRldwgVQcesnn2EwDTbCm")

print("\n4. 市场分析师:")
print("   API Key: 6EmtlQblz18ZjHNyFlHz2MlJJPT9egJUdAiTknCL8eUxs9drFwoHA7uGx16ZGRXIf")

print("\n5. 长期价值投资分析师:")
print("   API Key: 6oQxDcpeg1LLURAT35QWXodFPqNz8EXj6daOGk1IKxhDVv3HUi1UeClM5sHXxvs6z")

print("\n6. 首席经济学家:")
print("   API Key: 62RprR40Z99RnDlgP7Ho3geKQqI3hiE9MZ218AfjTpF4ZhJsA7bETmyCzmpNA7oRh")

print("\n【优势】")
print("✅ 每个专家使用独立的API Key")
print("✅ 避免并发调用同一个API端口导致超时")
print("✅ 提高系统稳定性和响应速度")
print("✅ 便于追踪和调试各专家的API调用情况")

print("\n【工作流程】")
print("用户打开'开始讨论'")
print("  ↓")
print("依次调用5个专家（串行）")
print("  ├─ 选股分析师 → 使用专属API Key 1")
print("  ├─ 产业链分析师 → 使用专属API Key 2")
print("  ├─ 市场分析师 → 使用专属API Key 3")
print("  ├─ 长期价值投资分析师 → 使用专属API Key 4")
print("  └─ 首席经济学家 → 使用专属API Key 5")
print("  ↓")
print("每个专家独立调用，互不干扰")

print("\n" + "="*70)
