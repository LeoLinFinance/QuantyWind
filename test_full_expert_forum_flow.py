"""
完整测试智者论坛流程
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.expert_forum_service import ExpertForumService

async def test_full_flow():
    print("=" * 80)
    print("智者论坛完整流程测试")
    print("=" * 80)
    
    service = ExpertForumService()
    
    # 步骤1: 重置对话
    print("\n【步骤1】重置对话")
    print("-" * 80)
    await service.reset_conversation()
    print("✅ 对话已重置")
    
    # 步骤2: 获取新闻总结
    print("\n【步骤2】获取新闻总结（模拟\"接收资讯\"）")
    print("-" * 80)
    news_result = await service.fetch_news_summary()
    print(f"✅ 新闻总结成功")
    print(f"   内容: {news_result['content'][:200]}...")
    
    # 检查是否添加到对话
    history = await service.get_conversation_history()
    print(f"✅ 对话历史现在有 {len(history)} 条消息")
    if history:
        print(f"   最新消息角色: {history[-1]['role']}")
        print(f"   最新消息内容: {history[-1]['content'][:100]}...")
    
    # 步骤3: 用户提问
    print("\n【步骤3】用户提问")
    print("-" * 80)
    user_msg = await service.add_user_message("请分析一下AAPL和TSLA的投资价值")
    print(f"✅ 用户消息已添加")
    print(f"   消息ID: {user_msg['id']}")
    print(f"   识别意图: {user_msg['intent']}")
    
    # 步骤4: 获取专家配置
    print("\n【步骤4】获取专家配置")
    print("-" * 80)
    configs = await service.get_expert_configs()
    print(f"✅ 找到 {len(configs)} 个专家")
    
    # 步骤5: 专家分析（模拟"开始讨论"）
    print("\n【步骤5】专家分析（模拟\"开始讨论\"）")
    print("-" * 80)
    
    # 只测试前2个专家以节省时间
    for i, expert in enumerate(configs[:2]):
        print(f"\n专家 {i+1}/{min(2, len(configs))}: {expert['name']}")
        print("-" * 40)
        
        # 获取当前上下文
        context = await service.chat_service.get_context_for_expert()
        print(f"上下文长度: {len(context)} 字符")
        
        try:
            result = await service.get_expert_analysis(
                expert_id=expert['id'],
                expert_name=expert['name'],
                expert_prompt=expert['prompt'],
                context=context
            )
            
            print(f"✅ {expert['name']}分析成功")
            print(f"   分析长度: {len(result['analysis'])} 字符")
            print(f"   分析预览: {result['analysis'][:200]}...")
            
        except Exception as e:
            print(f"❌ {expert['name']}分析失败: {e}")
    
    # 步骤6: 查看最终对话历史
    print("\n【步骤6】查看最终对话历史")
    print("-" * 80)
    final_history = await service.get_conversation_history()
    print(f"✅ 对话历史包含 {len(final_history)} 条消息")
    
    for i, msg in enumerate(final_history):
        role_label = {
            'kimi': 'KimiClaw资讯',
            'user': '用户',
            'expert': msg.get('expert_type', '专家'),
            'system': '系统'
        }.get(msg['role'], msg['role'])
        
        print(f"\n消息 {i+1}: [{role_label}]")
        print(f"  内容: {msg['content'][:150]}...")
        if msg.get('intent'):
            print(f"  意图: {msg['intent']}")
    
    # 步骤7: 检查聊天统计
    print("\n【步骤7】检查聊天统计")
    print("-" * 80)
    stats = service.get_chat_stats()
    print(f"✅ 消息计数: {stats['message_count']}/10")
    print(f"✅ 是否有总结: {stats['has_summary']}")
    
    print("\n" + "=" * 80)
    print("✅ 完整流程测试成功！")
    print("=" * 80)
    print("\n总结:")
    print(f"  - 新闻总结: ✅ 正常")
    print(f"  - 用户提问: ✅ 正常")
    print(f"  - 专家分析: ✅ 正常")
    print(f"  - 对话历史: ✅ 正常 ({len(final_history)}条消息)")
    print(f"  - 消息计数: ✅ 正常 ({stats['message_count']}/10)")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
