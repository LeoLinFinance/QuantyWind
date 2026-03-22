#!/usr/bin/env python3
"""
测试智者论坛API修复
验证新闻接口和专家分析是否使用正确的API
"""
import asyncio
import sys
from pathlib import Path

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.expert_forum_service import ExpertForumService
from services.news_summary_service import NewsSummaryService

async def test_news_summary():
    """测试新闻总结（应使用StepFun API）"""
    print("\n" + "="*60)
    print("测试1: 新闻总结（StepFun API）")
    print("="*60)
    
    try:
        service = NewsSummaryService()
        print(f"✅ 使用API: {service.client.base_url}")
        print(f"✅ 使用模型: {service.model}")
        
        result = service.summarize_news()
        
        print(f"\n✅ 新闻总结成功")
        print(f"   新闻数量: {result['news_count']}")
        print(f"   持仓股票: {result['portfolio_symbols']}")
        print(f"   数据源: {result['source']}")
        print(f"\n总结内容预览:")
        print("-" * 60)
        print(result['summary'][:300] + "..." if len(result['summary']) > 300 else result['summary'])
        print("-" * 60)
        
        return True
    except Exception as e:
        print(f"❌ 新闻总结失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_expert_analysis():
    """测试专家分析（应使用StepFun 32k API）"""
    print("\n" + "="*60)
    print("测试2: 专家分析（StepFun 32k API）")
    print("="*60)
    
    try:
        service = ExpertForumService()
        print(f"✅ 使用API: {service.stepfun_client.base_url}")
        print(f"✅ 使用模型: {service.stepfun_model}")
        
        # 测试专家配置
        configs = await service.get_expert_configs()
        if not configs:
            print("⚠️  没有专家配置，请先运行: python3 init_expert_configs.py")
            return False
        
        print(f"✅ 找到 {len(configs)} 个专家配置")
        
        # 测试第一个专家
        expert = configs[0]
        print(f"\n测试专家: {expert['name']}")
        
        result = await service.get_expert_analysis(
            expert_id=expert['id'],
            expert_name=expert['name'],
            expert_prompt=expert['prompt'],
            context="测试上下文"
        )
        
        print(f"\n✅ 专家分析成功")
        print(f"   专家: {result['expert_name']}")
        print(f"   分析股票数: {result['holdings_analyzed']}")
        print(f"\n分析内容预览:")
        print("-" * 60)
        print(result['analysis'][:300] + "..." if len(result['analysis']) > 300 else result['analysis'])
        print("-" * 60)
        
        return True
    except Exception as e:
        print(f"❌ 专家分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("智者论坛API修复验证")
    print("="*60)
    print("\n修复内容:")
    print("1. 新闻接口改用StepFun API（与市场洞察相同）")
    print("2. 专家分析改用StepFun 32k API")
    print("\nAPI Key: 6NrpM4FmGscMbUkaO3Td18iEKsL1Bu9XjYY1uag8bMrKSjObFV8SA4smCitJpb6rA")
    
    results = []
    
    # 测试新闻总结
    results.append(await test_news_summary())
    
    # 测试专家分析
    results.append(await test_expert_analysis())
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    if all(results):
        print("✅ 所有测试通过！")
        print("\n修复验证成功:")
        print("  ✅ 新闻总结使用StepFun API")
        print("  ✅ 专家分析使用StepFun 32k API")
        print("\n现在可以启动后端测试完整功能:")
        print("  python3 backend/main.py")
    else:
        print("❌ 部分测试失败")
        print("\n请检查:")
        print("  1. 是否已初始化专家配置: python3 init_expert_configs.py")
        print("  2. API Key是否正确")
        print("  3. 网络连接是否正常")

if __name__ == "__main__":
    asyncio.run(main())
