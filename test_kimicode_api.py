"""
测试Kimi Code API连接
"""
import requests
import json

# Kimi Code API配置
API_ID = "19cfa732-1992-84ae-8000-0000fdd3981a"
API_KEY = "sk-kimi-DgJ03a0Yyr4mo66Q7RBTfoeNjm2UlbrfNrPPHr1r85v3txsvhdZIfOA7Q426ijt0"

def test_kimicode_api():
    """测试Kimi Code API - 尝试多种可能的端点"""
    
    print("=" * 60)
    print("测试Kimi Code API连接")
    print("=" * 60)
    print(f"\nAPI ID: {API_ID}")
    
    # 测试查询
    test_query = "请简要总结一下今天美股市场的表现"
    
    # 尝试不同的API端点格式
    api_urls = [
        f"https://api.moonshot.cn/v1/services/{API_ID}/run",
        f"https://api.moonshot.cn/v1/agents/{API_ID}/run",
        f"https://api.moonshot.cn/v1/bots/{API_ID}/run",
        "https://api.moonshot.cn/v1/chat/completions",  # 标准chat端点
    ]
    
    for i, api_url in enumerate(api_urls, 1):
        print(f"\n尝试 {i}/{len(api_urls)}: {api_url}")
        print("-" * 60)
        
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 根据不同端点使用不同的数据格式
        if 'chat/completions' in api_url:
            data = {
                'model': 'moonshot-v1-8k',
                'messages': [
                    {'role': 'user', 'content': test_query}
                ],
                'tools': [
                    {
                        'type': 'builtin_function',
                        'function': {'name': '$web_search'}
                    }
                ]
            }
        else:
            data = {
                'inputs': {'query': test_query}
            }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ API调用成功!")
                print("\n响应内容:")
                print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
                return True, api_url
            else:
                print(f"错误: {response.text[:200]}")
                
        except Exception as e:
            print(f"异常: {type(e).__name__}: {e}")
    
    return False, None

if __name__ == "__main__":
    success, working_url = test_kimicode_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Kimi Code API测试通过，可以集成到系统中")
        print(f"工作的API端点: {working_url}")
    else:
        print("❌ Kimi Code API测试失败，请检查配置")
    print("=" * 60)
