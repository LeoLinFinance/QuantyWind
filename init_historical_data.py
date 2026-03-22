#!/usr/bin/env python3
"""
初始化历史数据
使用yfinance获取股票和指数的历史数据
"""
import sys
sys.path.insert(0, 'backend')

from services.historical_data_service import HistoricalDataService
import yfinance as yf
from datetime import datetime, timedelta

def init_historical_data():
    """初始化历史数据"""
    service = HistoricalDataService()
    
    # 盯盘股票列表
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
    
    # 指数列表
    indices = {
        '^IXIC': '纳斯达克',
        '^GSPC': '标普500',
        '^RUT': '罗素2000'
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 获取一年数据
    
    print("="*60)
    print("开始初始化历史数据")
    print("="*60)
    print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print(f"股票数量: {len(symbols)}")
    print(f"指数数量: {len(indices)}")
    print()
    
    # 初始化指数数据
    print("📊 初始化指数数据...")
    print("-"*60)
    for symbol, name in indices.items():
        try:
            print(f"获取 {name}({symbol}) 数据...", end=" ")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                print(f"❌ 无数据")
                continue
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            service.data['indices'][symbol] = {
                'symbol': symbol,
                'name': name,
                'data': data,
                'last_update': datetime.now().isoformat()
            }
            print(f"✅ {len(data)} 条数据")
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    # 初始化股票数据
    print("\n📈 初始化股票数据...")
    print("-"*60)
    for symbol in symbols:
        try:
            print(f"获取 {symbol} 数据...", end=" ")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                print(f"❌ 无数据")
                continue
            
            try:
                info = ticker.info
                name = info.get('longName', symbol)
            except:
                name = symbol
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            service.data['stocks'][symbol] = {
                'symbol': symbol,
                'name': name,
                'data': data,
                'last_update': datetime.now().isoformat(),
                'is_active': True
            }
            print(f"✅ {len(data)} 条数据")
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    # 更新元数据
    service.data['metadata']['last_update'] = datetime.now().isoformat()
    service.data['metadata']['data_source'] = 'yfinance'
    
    # 保存数据
    print("\n💾 保存数据...")
    print("-"*60)
    service.save_data()
    
    print("\n" + "="*60)
    print("✅ 历史数据初始化完成!")
    print("="*60)
    print(f"数据文件: {service.data_file}")
    print(f"股票数量: {len(service.data['stocks'])}")
    print(f"指数数量: {len(service.data['indices'])}")
    
    # 显示数据摘要
    print("\n📋 数据摘要:")
    print("-"*60)
    for symbol, info in service.data['stocks'].items():
        data_count = len(info.get('data', []))
        print(f"  {symbol:6s} - {info['name']:30s} - {data_count:3d} 条数据")
    
    return True

if __name__ == "__main__":
    try:
        success = init_historical_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
