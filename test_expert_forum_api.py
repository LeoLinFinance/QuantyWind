"""
测试智者论坛API
"""
import sys
sys.path.insert(0, 'backend')

import asyncio
import logging
from services.expert_forum_service import ExpertForumService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_news_summary():
    """测试新闻总结功能"""
    print("\n" + "="*60)
    print("测试1: 新闻总结功能")
    print("="*60)
    
    service = ExpertForumService()
    
    try:
        result = await service.fetch_news_summary()
        print(f"\n✅ 新闻总结成功!")
        print(f"内容长度: {len(result['content'])} 字符")
        print(f"新闻数量: {result['news_count']}")
        print(f"持仓股票: {result['stock_symbols']}")
        print(f"\n总结内容预览:")
        print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
        return True
    except Exception as e:
        print(f"\n❌ 新闻总结失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_expert_analysis():
    """测试专家分析功能"""
    print("\n" + "="*60)
    print("测试2: 专家分析功能")
    print("="*60)
    
    service = ExpertForumService()
    
    # 模拟一个简单的上下文
    context = "[kimi] 今日市场整体上涨，科技股表现强劲。"
    
    try:
        result = await service.get_expert_analysis(
            expert_id="test_analyst",
            expert_name="测试分析师",
            expert_prompt="请简要分析当前市场情况",
            context=context
        )
        print(f"\n✅ 专家分析成功!")
        print(f"专家: {result['expert_name']}")
        print(f"分析长度: {len(result['analysis'])} 字符")
        print(f"\n分析内容预览:")
        print(result['analysis'][:500] + "..." if len(result['analysis']) > 500 else result['analysis'])
        return True
    except Exception as e:
        print(f"\n❌ 专家分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("\n🔍 开始测试智者论坛API...")
    
    # 测试新闻总结
    news_ok = await test_news_summary()
    
    # 等待一下避免API限流
    await asyncio.sleep(2)
    
    # 测试专家分析
    expert_ok = await test_expert_analysis()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"新闻总结: {'✅ 通过' if news_ok else '❌ 失败'}")
    print(f"专家分析: {'✅ 通过' if expert_ok else '❌ 失败'}")
    
    if news_ok and expert_ok:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    asyncio.run(main())
