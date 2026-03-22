#!/usr/bin/env python3
"""
详细测试AI信号服务，捕获具体错误
"""
import sys
sys.path.insert(0, 'backend')

from services.ai_signals_service import AISignalsService
import traceback

def test_analyze_stock(symbol: str):
    """测试股票分析"""
    print(f"\n{'='*60}")
    print(f"测试股票分析: {symbol}")
    print(f"{'='*60}")
    
    try:
        service = AISignalsService()
        print(f"✅ AI信号服务初始化成功")
        
        print(f"\n开始分析 {symbol}...")
        result = service.analyze_stock(symbol)
        
        print(f"\n✅ 分析成功!")
        print(f"当前价格: ${result.get('current_price', 'N/A')}")
        print(f"综合评分: {result.get('analysis', {}).get('overall_score', 'N/A')}")
        print(f"数据来源: {result.get('data_sources', {})}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 分析失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"\n详细堆栈:")
        traceback.print_exc()
        return False

def test_trading_signal(symbol: str):
    """测试交易信号"""
    print(f"\n{'='*60}")
    print(f"测试交易信号: {symbol}")
    print(f"{'='*60}")
    
    try:
        service = AISignalsService()
        print(f"✅ AI信号服务初始化成功")
        
        print(f"\n开始生成交易信号 {symbol}...")
        result = service.generate_trading_signal(symbol)
        
        print(f"\n✅ 信号生成成功!")
        print(f"信号类型: {result.get('signal', 'N/A')}")
        print(f"置信度: {result.get('confidence', 'N/A')}%")
        print(f"目标价: ${result.get('target_price', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 信号生成失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"\n详细堆栈:")
        traceback.print_exc()
        return False

def main():
    print("🔍 详细测试AI信号服务")
    
    test_symbols = ["AAPL"]
    
    for symbol in test_symbols:
        # 测试分析
        success1 = test_analyze_stock(symbol)
        
        # 测试信号
        success2 = test_trading_signal(symbol)
        
        if success1 and success2:
            print(f"\n✅ {symbol} 所有测试通过")
        else:
            print(f"\n❌ {symbol} 测试失败")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
