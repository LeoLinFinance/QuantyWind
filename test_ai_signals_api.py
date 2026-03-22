#!/usr/bin/env python3
"""
测试AI信号API是否正常工作
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_api_endpoint(endpoint, method="GET", data=None):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"测试: {method} {endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 请求成功")
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
            return True
        else:
            print(f"❌ 请求失败")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确认后端服务是否在8000端口运行")
        print("   启动命令: cd backend && python3 main.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def main():
    print("🔍 开始测试AI信号API")
    print(f"后端地址: {BASE_URL}")
    
    # 测试根路径
    if not test_api_endpoint("/"):
        print("\n❌ 后端服务未启动或无法访问")
        sys.exit(1)
    
    # 测试股票分析API
    test_symbols = ["AAPL", "TSLA", "NVDA"]
    
    for symbol in test_symbols:
        # 测试AI分析
        success = test_api_endpoint(f"/api/ai-signals/analyze/{symbol}")
        if not success:
            print(f"\n⚠️  {symbol} AI分析失败，可能原因：")
            print("   1. API密钥未配置或无效")
            print("   2. 数据不足")
            print("   3. 网络问题")
        
        # 测试交易信号
        success = test_api_endpoint(f"/api/ai-signals/trading-signal/{symbol}")
        if not success:
            print(f"\n⚠️  {symbol} 交易信号生成失败")
    
    # 测试提示词管理
    test_api_endpoint("/api/ai-signals/prompts")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
