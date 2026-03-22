"""
测试快速咨询专家功能
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.expert_forum_service import ExpertForumService

async def test_quick_consult():
    """测试快速咨询单个专家"""
    
    print("=" * 60)
    print("测试快速咨询专家功能")
    print("=" * 60)
    
    service = ExpertForumService()
    
    # 测试选股分析师
    print("\n测试1: 调用选股分析师")
    print("-" * 60)
    
    try:
        result = await service.get_expert_analysis(
            expert_id='stock_analyst',
            expert_name='选股分析师',
            expert_prompt='你是一位资深选股分析师，专注于投前分析。根据产业链状况、行业政策与前景、股票标的的近期表现以及财报等，综合推荐5-10只美股和港股。请提供具体的股票代码、推荐理由和风险提示。',
            context='暂无最新资讯'
        )
        
        if result:
            print(f"✅ 成功获取分析")
            print(f"专家: {result['expert_name']}")
            print(f"分析长度: {len(result['analysis'])} 字符")
            print(f"分析预览: {result['analysis'][:200]}...")
        else:
            print("⚠️ 专家选择不回复")
            
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_quick_consult())
