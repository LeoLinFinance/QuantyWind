#!/usr/bin/env python3
"""
测试yfinance是否正常工作
"""

import sys
from datetime import datetime, timedelta

try:
    import yfinance as yf
    import pandas as pd
    print("✅ yfinance导入成功")
    print(f"版本: {yf.__version__}")
except ImportError as e:
    print(f"❌ yfinance导入失败: {e}")
    print("请先安装: pip3 install yfinance")
    sys.exit(1)

print("\n" + "="*60)
print("测试1: 获取AAPL最近30天数据")
print("="*60)

try:
    ticker = yf.Ticker('AAPL')
    start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end = datetime.now().strftime('%Y-%m-%d')
    
    df = ticker.history(start=start, end=end)
    
    if df.empty:
        print("❌ 未获取到数据")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print("\n最近5天数据:")
        print(df.tail())
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("\n" + "="*60)
print("测试2: 获取纳斯达克指数数据")
print("="*60)

try:
    ticker = yf.Ticker('^IXIC')
    start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end = datetime.now().strftime('%Y-%m-%d')
    
    df = ticker.history(start=start, end=end)
    
    if df.empty:
        print("❌ 未获取到数据")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print(f"最新收盘价: {df['Close'].iloc[-1]:.2f}")
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("\n" + "="*60)
print("测试3: 获取10年历史数据")
print("="*60)

try:
    ticker = yf.Ticker('MSFT')
    start = (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')
    end = datetime.now().strftime('%Y-%m-%d')
    
    df = ticker.history(start=start, end=end)
    
    if df.empty:
        print("❌ 未获取到数据")
    else:
        print(f"✅ 成功获取 {len(df)} 条数据")
        print(f"日期范围: {df.index[0].strftime('%Y-%m-%d')} 到 {df.index[-1].strftime('%Y-%m-%d')}")
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("\n" + "="*60)
print("测试完成！")
print("="*60)
print("\n如果所有测试都通过，说明yfinance工作正常。")
print("现在可以重启后端服务并测试历史数据更新功能。\n")
