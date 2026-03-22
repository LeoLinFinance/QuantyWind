"""
诊断智者论坛问题
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.expert_forum_service import ExpertForumService

async def diagnose():
    print("=" * 80)
    print("智者论坛诊断工具")
    print("=" * 80)
    
    service = ExpertForumService()
    
    # 测试1: 获取新闻总结
    print("\n【测试1】获取新闻总结")
    print("-" * 80)
    try:
        news_result = await service.fetch_news_summary()
        print(f"✅ 新闻总结成功")
        print(f"   内容长度: {len(news_result['content'])} 字符")
        print(f"   内容预览: {news_result['content'][:200]}...")
        print(f"   时间戳: {news_result['timestamp']}")
        print(f"   相关股票: {news_result['stock_symbols']}")
    except Exception as e:
        print(f"❌ 新闻总结失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 检查专家配置
    print("\n【测试2】检查专家配置")
    print("-" * 80)
    try:
        configs = await service.get_expert_configs()
        print(f"✅ 找到 {len(configs)} 个专家配置")
        for config in configs:
            print(f"   - {config['name']} (ID: {config['id']})")
            print(f"     提示词长度: {len(config['prompt'])} 字符")
    except Exception as e:
        print(f"❌ 获取专家配置失败: {e}")
    
    # 测试3: 测试专家分析（使用第一个专家）
    print("\n【测试3】测试专家分析")
    print("-" * 80)
    if configs:
        expert = configs[0]
        print(f"使用专家: {expert['name']}")
        
        # 构建测试上下文
        test_context = "[kimi] 测试资讯：市场今日上涨"
        
        try:
            print(f"调用专家分析...")
            print(f"  专家ID: {expert['id']}")
            print(f"  专家名称: {expert['name']}")
            print(f"  提示词: {expert['prompt'][:100]}...")
            print(f"  上下文: {test_context}")
            
            result = await service.get_expert_analysis(
                expert_id=expert['id'],
                expert_name=expert['name'],
                expert_prompt=expert['prompt'],
                context=test_context
            )
            
            print(f"✅ 专家分析成功")
            print(f"   分析长度: {len(result['analysis'])} 字符")
            print(f"   分析预览: {result['analysis'][:300]}...")
            print(f"   时间戳: {result['timestamp']}")
            
        except Exception as e:
            print(f"❌ 专家分析失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试4: 检查聊天服务
    print("\n【测试4】检查聊天服务")
    print("-" * 80)
    try:
        history = await service.get_conversation_history()
        print(f"✅ 对话历史包含 {len(history)} 条消息")
        
        stats = service.get_chat_stats()
        print(f"✅ 聊天统计:")
        print(f"   消息计数: {stats['message_count']}")
        print(f"   是否有总结: {stats['has_summary']}")
        
    except Exception as e:
        print(f"❌ 聊天服务检查失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试5: 检查Kimi服务
    print("\n【测试5】检查Kimi服务")
    print("-" * 80)
    try:
        kimi_service = service.kimi_service
        print(f"✅ Kimi服务已初始化")
        print(f"   API Key配置: {'是' if kimi_service.api_key else '否'}")
        print(f"   Base URL: {kimi_service.base_url}")
        
        # 测试简单调用
        test_query = "你好，请简单回复一下"
        print(f"\n测试Kimi调用: {test_query}")
        response = kimi_service._call_kimi_with_search(test_query, max_tokens=50)
        print(f"✅ Kimi响应: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ Kimi服务检查失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(diagnose())
