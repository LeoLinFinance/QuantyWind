#!/usr/bin/env python3
"""
AI信号功能诊断脚本
检查所有可能导致功能失效的问题
"""
import os
import sys
from pathlib import Path

def check_env_file():
    """检查环境变量配置"""
    print("\n📋 检查环境变量配置...")
    print("-" * 60)
    
    if not os.path.exists('.env'):
        print("❌ .env文件不存在")
        print("   请复制.env.example并配置API密钥")
        return False
    
    print("✅ .env文件存在")
    
    # 检查关键环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    stepfun_key = os.getenv('STEPFUN_API_KEY')
    kimi_key = os.getenv('KIMI_API_KEY')
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not stepfun_key or stepfun_key == 'your_stepfun_api_key_here':
        print("⚠️  STEPFUN_API_KEY 未配置或使用默认值")
    else:
        print(f"✅ STEPFUN_API_KEY 已配置 ({stepfun_key[:10]}...)")
    
    if not kimi_key or kimi_key == 'your_kimi_api_key_here':
        print("⚠️  KIMI_API_KEY 未配置或使用默认值")
    else:
        print(f"✅ KIMI_API_KEY 已配置 ({kimi_key[:10]}...)")
    
    if not alpha_key or alpha_key == 'your_alpha_vantage_api_key_here':
        print("⚠️  ALPHA_VANTAGE_API_KEY 未配置或使用默认值")
    else:
        print(f"✅ ALPHA_VANTAGE_API_KEY 已配置 ({alpha_key[:10]}...)")
    
    if (not stepfun_key or stepfun_key == 'your_stepfun_api_key_here') and \
       (not kimi_key or kimi_key == 'your_kimi_api_key_here'):
        print("\n❌ 至少需要配置 STEPFUN_API_KEY 或 KIMI_API_KEY 之一")
        return False
    
    return True

def check_backend_structure():
    """检查后端文件结构"""
    print("\n📁 检查后端文件结构...")
    print("-" * 60)
    
    required_files = [
        'backend/main.py',
        'backend/routers/ai_signals.py',
        'backend/services/ai_signals_service.py',
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def check_frontend_structure():
    """检查前端文件结构"""
    print("\n📁 检查前端文件结构...")
    print("-" * 60)
    
    required_files = [
        'src/pages/MarketInsightPage.tsx',
        'src/components/AIAnalysisModal.tsx',
        'src/components/TradingSignalCard.tsx',
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """检查Python依赖"""
    print("\n📦 检查Python依赖...")
    print("-" * 60)
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'requests',
        'python-dotenv',
        'numpy',
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_installed = False
    
    return all_installed

def check_port_availability():
    """检查端口是否可用"""
    print("\n🔌 检查端口状态...")
    print("-" * 60)
    
    import socket
    
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    backend_port = 8000
    frontend_port = 3000
    
    if is_port_in_use(backend_port):
        print(f"✅ 后端端口 {backend_port} 正在使用（服务可能已启动）")
    else:
        print(f"⚠️  后端端口 {backend_port} 未使用（服务未启动）")
        print(f"   启动命令: cd backend && python3 main.py")
    
    if is_port_in_use(frontend_port):
        print(f"✅ 前端端口 {frontend_port} 正在使用（服务可能已启动）")
    else:
        print(f"⚠️  前端端口 {frontend_port} 未使用（服务未启动）")
        print(f"   启动命令: npm run dev")

def test_ai_service():
    """测试AI服务初始化"""
    print("\n🤖 测试AI服务...")
    print("-" * 60)
    
    try:
        sys.path.insert(0, 'backend')
        from services.ai_signals_service import AISignalsService
        
        service = AISignalsService()
        print("✅ AI服务初始化成功")
        return True
    except Exception as e:
        print(f"❌ AI服务初始化失败: {e}")
        return False

def main():
    print("="*60)
    print("🔍 AI信号功能诊断")
    print("="*60)
    
    results = {
        '环境变量': check_env_file(),
        '后端结构': check_backend_structure(),
        '前端结构': check_frontend_structure(),
        'Python依赖': check_dependencies(),
    }
    
    check_port_availability()
    results['AI服务'] = test_ai_service()
    
    print("\n" + "="*60)
    print("📊 诊断结果汇总")
    print("="*60)
    
    for check, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{check}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ 所有检查通过！")
        print("\n下一步：")
        print("1. 确保后端服务已启动: cd backend && python3 main.py")
        print("2. 确保前端服务已启动: npm run dev")
        print("3. 运行API测试: python3 test_ai_signals_api.py")
    else:
        print("\n❌ 存在问题需要修复")
        print("\n请根据上述错误信息进行修复")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
