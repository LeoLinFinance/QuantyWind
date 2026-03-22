"""
检查后端状态和API连接
"""
import requests
import json

def check_backend():
    print("=" * 80)
    print("检查后端状态")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # 1. 检查后端是否运行
    print("\n【1】检查后端是否运行...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ 后端正在运行 (状态码: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ 后端未运行！请先启动后端: python3 backend/main.py")
        return
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return
    
    # 2. 检查专家配置
    print("\n【2】检查专家配置...")
    try:
        response = requests.get(f"{base_url}/api/expert-forum/configs", timeout=5)
        if response.status_code == 200:
            configs = response.json()
            print(f"✅ 找到 {len(configs)} 个专家配置")
            for config in configs:
                print(f"   - {config['name']}")
        else:
            print(f"❌ 获取配置失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 3. 测试获取新闻
    print("\n【3】测试获取新闻...")
    try:
        response = requests.post(
            f"{base_url}/api/expert-forum/news",
            json={"last_time": None},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 新闻获取成功")
            print(f"   内容长度: {len(data.get('content', ''))} 字符")
            print(f"   内容预览: {data.get('content', '')[:100]}...")
        else:
            print(f"❌ 新闻获取失败 (状态码: {response.status_code})")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 4. 检查对话历史
    print("\n【4】检查对话历史...")
    try:
        response = requests.get(f"{base_url}/api/expert-forum/messages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            print(f"✅ 对话历史包含 {len(messages)} 条消息")
            for i, msg in enumerate(messages[-5:]):  # 显示最后5条
                print(f"   {i+1}. [{msg['role']}] {msg['content'][:50]}...")
        else:
            print(f"❌ 获取历史失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 5. 测试专家分析（使用第一个专家）
    print("\n【5】测试专家分析（这可能需要30-45秒）...")
    try:
        # 先获取配置
        response = requests.get(f"{base_url}/api/expert-forum/configs", timeout=5)
        if response.status_code == 200:
            configs = response.json()
            if configs:
                expert = configs[0]
                print(f"   使用专家: {expert['name']}")
                
                response = requests.post(
                    f"{base_url}/api/expert-forum/expert-analysis",
                    json={
                        "expert_id": expert['id'],
                        "expert_name": expert['name'],
                        "expert_prompt": expert['prompt'],
                        "context": "[kimi] 测试资讯"
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 专家分析成功")
                    print(f"   分析长度: {len(data.get('analysis', ''))} 字符")
                    print(f"   分析预览: {data.get('analysis', '')[:100]}...")
                else:
                    print(f"❌ 专家分析失败 (状态码: {response.status_code})")
                    print(f"   响应: {response.text[:200]}")
            else:
                print("❌ 没有专家配置")
    except requests.exceptions.Timeout:
        print("❌ 请求超时（60秒）")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)

if __name__ == "__main__":
    check_backend()
