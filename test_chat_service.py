"""
测试智者论坛聊天服务
"""
import asyncio
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.expert_forum_chat_service import ExpertForumChatService
from backend.models.message import MessageRole

async def test_chat_service():
    """测试聊天服务的基本功能"""
    print("=" * 60)
    print("测试智者论坛聊天服务")
    print("=" * 60)
    
    # 初始化服务
    print("\n1. 初始化聊天服务...")
    chat_service = ExpertForumChatService()
    print("✅ 聊天服务初始化成功")
    
    # 测试添加新闻总结
    print("\n2. 添加新闻总结...")
    news_message = await chat_service.add_news_summary(
        "今日市场概况：美股三大指数集体上涨，科技股表现强劲。特斯拉涨3.5%，苹果涨2.1%。",
        stock_symbols=["TSLA", "AAPL"]
    )
    print(f"✅ 新闻消息已添加: {news_message.id}")
    print(f"   消息计数: {chat_service.get_message_count()}")
    
    # 测试添加用户消息
    print("\n3. 添加用户消息...")
    user_message = await chat_service.add_user_message(
        "请分析一下当前市场走势，我应该买入还是持有？"
    )
    print(f"✅ 用户消息已添加: {user_message.id}")
    print(f"   识别意图: {user_message.intent.value if user_message.intent else 'None'}")
    print(f"   消息计数: {chat_service.get_message_count()}")
    
    # 测试添加专家回复
    print("\n4. 添加专家回复...")
    expert_message = await chat_service.add_expert_response(
        expert_type="首席经济学家",
        content="根据当前市场情况，建议采取谨慎乐观的态度。科技股表现强劲是积极信号，但需要关注宏观经济数据。"
    )
    print(f"✅ 专家回复已添加: {expert_message.id}")
    print(f"   专家类型: {expert_message.expert_type}")
    print(f"   消息计数: {chat_service.get_message_count()}")
    
    # 测试获取上下文
    print("\n5. 获取专家上下文...")
    context = await chat_service.get_context_for_expert()
    print("✅ 上下文内容:")
    print("-" * 60)
    print(context)
    print("-" * 60)
    
    # 测试获取对话历史
    print("\n6. 获取对话历史...")
    history = await chat_service.get_conversation_history()
    print(f"✅ 对话历史包含 {len(history)} 条消息")
    for msg in history:
        print(f"   [{msg.role.value}] {msg.content[:50]}...")
    
    # 测试消息计数
    print("\n7. 测试消息计数和总结触发...")
    print(f"   当前消息数: {chat_service.get_message_count()}")
    print(f"   是否有总结: {chat_service.has_active_summary()}")
    
    # 添加更多消息以测试总结功能（需要超过10条）
    print("\n8. 添加更多消息测试总结功能...")
    for i in range(8):
        await chat_service.add_user_message(f"测试消息 {i+1}")
        print(f"   添加消息 {i+1}, 当前计数: {chat_service.get_message_count()}")
    
    print(f"\n   最终消息数: {chat_service.get_message_count()}")
    print(f"   是否有总结: {chat_service.has_active_summary()}")
    
    if chat_service.has_active_summary():
        print("   ⚠️  注意：消息数超过10条，应该触发总结（需要配置StepFun API）")
    
    # 测试重置对话
    print("\n9. 测试重置对话...")
    await chat_service.reset_conversation()
    history_after_reset = await chat_service.get_conversation_history()
    print(f"✅ 对话已重置，当前消息数: {len(history_after_reset)}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_chat_service())
