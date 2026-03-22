"""
测试Kimi-k2 API连接
"""
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key="sk-YqINSKAInLWLWRxnFmUO14Jwc4RpkKiydsM0GzDWc4ohhyja",
    base_url="https://api.moonshot.cn/v1"
)

def test_kimi_k2():
    """测试Kimi-k2 API"""
    
    print("=" * 60)
    print("测试Kimi-k2 API连接")
    print("=" * 60)
    
    # 声明使用内置的 web_search 工具
    tools = [{
        "type": "builtin_function", 
        "function": {"name": "$web_search"}
    }]
    
    # 测试查询
    test_query = "搜索今天美股市场的最新动态和重要新闻"
    
    print(f"\n发送测试查询: {test_query}")
    print("-" * 60)
    
    try:
        # 第一次请求
        messages = [{"role": "user", "content": test_query}]
        
        response = client.chat.completions.create(
            model="kimi-k2-turbo-preview",
            messages=messages,
            tools=tools
        )
        
        print("\n✅ 第一次API调用成功!")
        
        # 提取回复内容
        if response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            
            # 检查是否有tool_calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print("\n🔍 检测到工具调用，需要第二次请求获取最终结果")
                
                # 将assistant的消息添加到对话历史
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                })
                
                # 添加tool响应（空响应，让模型继续）
                for tool_call in message.tool_calls:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": ""
                    })
                
                # 第二次请求获取最终结果
                print("\n发送第二次请求...")
                final_response = client.chat.completions.create(
                    model="kimi-k2-turbo-preview",
                    messages=messages,
                    tools=tools
                )
                
                print("\n✅ 第二次API调用成功!")
                print("\n📝 最终回复内容:")
                print("-" * 60)
                
                if final_response.choices and len(final_response.choices) > 0:
                    final_content = final_response.choices[0].message.content
                    print(final_content)
                    
                    print("\n" + "-" * 60)
                    print(f"总tokens使用: {final_response.usage.total_tokens if final_response.usage else 'N/A'}")
                
            elif message.content:
                print(f"\n📝 回复内容:\n{message.content}")
                print("\n" + "-" * 60)
                print(f"使用tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API调用失败: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_kimi_k2()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Kimi-k2 API测试通过，可以集成到系统中")
    else:
        print("❌ Kimi-k2 API测试失败，请检查配置")
    print("=" * 60)
