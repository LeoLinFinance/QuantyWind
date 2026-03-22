#!/usr/bin/env python3
"""
使用模拟数据初始化历史数据
用于测试AI分析功能
"""
import json
import os
from datetime import datetime, timedelta
import random

def generate_mock_price_data(symbol: str, days: int = 365, base_price: float = 100.0):
    """生成模拟价格数据"""
    data = []
    current_price = base_price
    end_date = datetime.now()
    
    for i in range(days):
        date = end_date - timedelta(days=days-i-1)
        
        # 模拟价格波动
        change_percent = random.uniform(-0.03, 0.03)  # ±3%
        current_price = current_price * (1 + change_percent)
        
        # 生成OHLC数据
        open_price = current_price * random.uniform(0.98, 1.02)
        high_price = max(open_price, current_price) * random.uniform(1.00, 1.02)
        low_price = min(open_price, current_price) * random.uniform(0.98, 1.00)
        close_price = current_price
        volume = int(random.uniform(50000000, 150000000))
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
    
    return data, current_price

def init_mock_historical_data():
    """初始化模拟历史数据"""
    
    # 股票配置
    stocks_config = {
        'AAPL': {'name': 'Apple Inc.', 'base_price': 180.0},
        'MSFT': {'name': 'Microsoft Corporation', 'base_price': 380.0},
        'GOOGL': {'name': 'Alphabet Inc.', 'base_price': 140.0},
        'AMZN': {'name': 'Amazon.com Inc.', 'base_price': 170.0},
        'TSLA': {'name': 'Tesla Inc.', 'base_price': 200.0},
        'NVDA': {'name': 'NVIDIA Corporation', 'base_price': 800.0},
        'META': {'name': 'Meta Platforms Inc.', 'base_price': 480.0},
        'NFLX': {'name': 'Netflix Inc.', 'base_price': 600.0},
        'AMD': {'name': 'Advanced Micro Devices Inc.', 'base_price': 180.0},
        'INTC': {'name': 'Intel Corporation', 'base_price': 45.0},
    }
    
    # 指数配置
    indices_config = {
        '^IXIC': {'name': '纳斯达克', 'base_price': 16000.0},
        '^GSPC': {'name': '标普500', 'base_price': 5000.0},
        '^RUT': {'name': '罗素2000', 'base_price': 2000.0},
    }
    
    print("="*60)
    print("开始初始化模拟历史数据")
    print("="*60)
    print(f"股票数量: {len(stocks_config)}")
    print(f"指数数量: {len(indices_config)}")
    print()
    
    # 构建数据结构
    historical_data = {
        'metadata': {
            'last_update': datetime.now().isoformat(),
            'data_source': 'mock_data',
            'version': '1.0'
        },
        'indices': {},
        'stocks': {}
    }
    
    # 生成指数数据
    print("📊 生成指数数据...")
    print("-"*60)
    for symbol, config in indices_config.items():
        data, final_price = generate_mock_price_data(symbol, 365, config['base_price'])
        historical_data['indices'][symbol] = {
            'symbol': symbol,
            'name': config['name'],
            'data': data,
            'last_update': datetime.now().isoformat()
        }
        print(f"✅ {config['name']:15s} ({symbol:6s}): {len(data)} 条数据, 最新价格: ${final_price:.2f}")
    
    # 生成股票数据
    print("\n📈 生成股票数据...")
    print("-"*60)
    for symbol, config in stocks_config.items():
        data, final_price = generate_mock_price_data(symbol, 365, config['base_price'])
        historical_data['stocks'][symbol] = {
            'symbol': symbol,
            'name': config['name'],
            'data': data,
            'last_update': datetime.now().isoformat(),
            'is_active': True
        }
        print(f"✅ {symbol:6s} - {config['name']:35s}: {len(data)} 条数据, 最新价格: ${final_price:.2f}")
    
    # 确保目录存在
    os.makedirs('data', exist_ok=True)
    
    # 保存数据
    data_file = 'data/historical_data.json'
    print(f"\n💾 保存数据到 {data_file}...")
    print("-"*60)
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(historical_data, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(data_file) / 1024 / 1024  # MB
    
    print("\n" + "="*60)
    print("✅ 模拟历史数据初始化完成!")
    print("="*60)
    print(f"数据文件: {data_file}")
    print(f"文件大小: {file_size:.2f} MB")
    print(f"股票数量: {len(historical_data['stocks'])}")
    print(f"指数数量: {len(historical_data['indices'])}")
    print(f"数据天数: 365 天")
    print()
    print("⚠️  注意: 这是模拟数据，仅用于测试AI分析功能")
    print("   生产环境请使用真实的市场数据")
    
    return True

if __name__ == "__main__":
    try:
        success = init_mock_historical_data()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
