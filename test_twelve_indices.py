"""测试Twelve Data支持的指数符号"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_API_KEY')

def test_index_symbol(symbol, name):
    """测试单个指数符号"""
    url = 'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': 5,
        'apikey': TWELVE_DATA_KEY,
        'format': 'JSON'
    }
    
    print(f"\n测试 {name} ({symbol})...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == 'ok':
            print(f"  ✅ 成功！数据点: {len(data.get('values', []))}")
            return True
        else:
            print(f"  ❌ 失败: {data.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

# 测试各种可能的指数符号
test_cases = [
    # NASDAQ
    ('IXIC', 'NASDAQ Composite'),
    ('NDX', 'NASDAQ 100'),
    ('COMP', 'NASDAQ Composite'),
    
    # S&P 500
    ('SPX', 'S&P 500'),
    ('SPY', 'S&P 500 ETF'),
    ('GSPC', 'S&P 500'),
    
    # Russell 2000
    ('RUT', 'Russell 2000'),
    ('IWM', 'Russell 2000 ETF'),
]

print("="*60)
print("测试Twelve Data支持的指数符号")
print("="*60)

for symbol, name in test_cases:
    test_index_symbol(symbol, name)

print("\n" + "="*60)
print("测试完成")
print("="*60)
