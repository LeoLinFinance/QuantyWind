#!/usr/bin/env python3
"""
测试Alpha Vantage API集成
"""

import sys
import os
from datetime import datetime, timedelta

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

# 测试API key
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
if not api_key:
    print("❌ 未找到ALPHA_VANTAGE_API_KEY环境变量")
    print("请在.env文件中添加: ALPHA_VANTAGE_API_KEY=your_api_key")
    sys.exit(1)

print(f"✅ API key已设置: {api_key[:4]}...{api_key[-4:]}")

# 测试HistoricalDataService
print("\n" + "="*60)
print("测试HistoricalDataService")
print("="*60)

try:
    from services.historical_data_service import HistoricalDataService
    
    service = HistoricalDataService()
    
    # 测试获取AAPL最近30天数据
    print("\n测试1: 获取AAPL最近30天数据")
    print("-"*60)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    data = service._fetch_yahoo_history('AAPL', start_date, end_date)
    
    if data:
        print(f"✅ 成功获取 {len(data)} 条数据")
        print(f"日期范围: {data[0]['date']} 到 {data[-1]['date']}")
        print(f"最新收盘价: ${data[-1]['close']:.2f}")
        print(f"\n最近3天数据:")
        for item in data[-3:]:
            print(f"  {item['date']}: 开${item['open']:.2f} 高${item['high']:.2f} 低${item['low']:.2f} 收${item['close']:.2f} 量{item['volume']:,}")
    else:
        print("❌ 未获取到数据")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n如果测试成功，现在可以：")
    print("1. 重启后端服务: cd backend && python3 main.py")
    print("2. 打开浏览器测试历史数据更新功能")
    print("\n注意：首次更新12个标的需要约3分钟（API限流保护）")
    
except Exception as e:
    print(f"❌ 测试失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
