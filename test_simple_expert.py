"""
简单测试专家调用
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.expert_forum_service import ExpertForumService

async def test():
    print("测试专家调用...")
    service = ExpertForumService()
    
    # 获取第一个专家
    configs = await service.get_expert_configs()
    if not configs:
        print("❌ 没有专家配置")
        return
    
    expert = configs[0]
    print(f"使用专家: {expert['name']}")
    
    # 简单的上下文
    context = "[kimi] 市场今日上涨\n[user] 请分析"
    
    print("开始调用专家...")
    try:
        result = await asyncio.wait_for(
            service.get_expert_analysis(
                expert_id=expert['id'],
                expert_name=expert['name'],
                expert_prompt=expert['prompt'],
                context=context
            ),
            timeout=50.0  # 50秒超时
        )
        print(f"✅ 成功: {result['analysis'][:200]}...")
    except asyncio.TimeoutError:
        print("❌ 超时（50秒）")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
