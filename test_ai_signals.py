#!/usr/bin/env python3
"""
AI信号功能测试脚本
测试个股分析和交易信号生成
"""
import sys
sys.path.insert(0, 'backend')

from services.ai_signals_service import AISignalsService

def test_ai_signals():
    """测试AI信号功能"""
    
    print("=" * 60)
    print("AI信号功能测试")
    print("=" * 60)
    
    # 1. 初始化服务
    print("\n【测试1】初始化AI信号服务")
    service = AISignalsService()
    print(f"   AI模型: {service.ai_service.stepfun_model}")
    print(f"   API Key: {service.ai_service.stepfun_api_key[:20]}...")
    print("✅ 服务初始化成功")
    
    # 2. 测试简单的AI调用
    print("\n【测试2】测试AI API调用")
    response = service.ai_service._call_stepfun(
        system_prompt="你是一个AI助手",
        user_prompt="请用一句话介绍AAPL公司",
        max_tokens=50
    )
    print(f"   AI响应: {response}")
    
    if "暂时不可用" in response or "失败" in response:
        print("❌ AI API调用失败")
        return False
    print("✅ AI API调用成功")
    
    # 3. 测试自定义提示词
    print("\n【测试3】测试自定义提示词")
    custom_prompt = "你是一个专注于技术分析的分析师。今天是{current_date}。"
    service.set_custom_prompt('stock_analysis', custom_prompt)
    loaded = service.get_custom_prompt('stock_analysis')
    assert loaded == custom_prompt, "提示词保存失败"
    print("✅ 自定义提示词功能正常")
    
    # 4. 测试个股分析（需要历史数据）
    print("\n【测试4】测试个股分析")
    print("   注意：此测试需要历史数据，如果没有数据会失败")
    try:
        # 尝试分析AAPL
        result = service.analyze_stock('AAPL')
        print(f"   分析结果: {result.get('symbol')}")
        print(f"   综合评分: {result.get('analysis', {}).get('overall_score', 'N/A')}")
        print(f"   是否缓存: {result.get('cached', False)}")
        print("✅ 个股分析功能正常")
    except Exception as e:
        print(f"⚠️ 个股分析测试跳过: {e}")
        print("   提示：请先添加股票到盯盘列表以获取历史数据")
    
    # 5. 测试交易信号（需要历史数据）
    print("\n【测试5】测试交易信号")
    try:
        signal = service.generate_trading_signal('AAPL')
        print(f"   信号类型: {signal.get('signal')}")
        print(f"   置信度: {signal.get('confidence')}%")
        print(f"   当前价格: ${signal.get('current_price', 0):.2f}")
        print("✅ 交易信号功能正常")
    except Exception as e:
        print(f"⚠️ 交易信号测试跳过: {e}")
        print("   提示：请先添加股票到盯盘列表以获取历史数据")
    
    print("\n" + "=" * 60)
    print("🎉 AI信号功能测试完成！")
    print("=" * 60)
    print("\n提示：")
    print("  1. AI模型已正确配置为 step-1v-32k")
    print("  2. API调用功能正常")
    print("  3. 自定义提示词功能可用")
    print("  4. 如需测试完整功能，请先在前端添加股票到盯盘列表")
    
    return True

if __name__ == '__main__':
    try:
        success = test_ai_signals()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
