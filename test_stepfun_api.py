"""
测试StepFun API连接
"""
from openai import OpenAI

# 初始化StepFun客户端
client = OpenAI(
    api_key="6NrpM4FmGscMbUkaO3Td18iEKsL1Bu9XjYY1uag8bMrKSjObFV8SA4smCitJpb6rA",
    base_url="https://api.stepfun.com/v1"
)

def test_stepfun():
    """测试StepFun API"""
    
    print("=" * 60)
    print("测试StepFun API连接")
    print("=" * 60)
    
    # 测试查询
    test_query = "请简要总结一下今天美股市场的表现"
    
    print(f"\n发送测试查询: {test_query}")
    print("-" * 60)
    
    try:
        # 发送请求
        response = client.chat.completions.create(
            model="step-1-32k",
            messages=[{"role": "user", "content": test_query}],
            temperature=0.3
        )
        
        print("\n✅ API调用成功!")
        print("\n响应内容:")
        print("-" * 60)
        
        # 提取回复内容
        if response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            
            if message.content:
                print(f"\n📝 回复内容:\n{message.content}")
            
            print("\n" + "-" * 60)
            print(f"模型: {response.model}")
            print(f"使用tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API调用失败: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_stepfun()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ StepFun API测试通过，可以集成到系统中")
    else:
        print("❌ StepFun API测试失败，请检查配置")
    print("=" * 60)
