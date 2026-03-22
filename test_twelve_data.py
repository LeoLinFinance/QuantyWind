"""测试Twelve Data API"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_API_KEY')

def test_twelve_data():
    """测试Twelve Data API"""
    print(f"API Key: {TWELVE_DATA_KEY[:10]}...")
    
    # 测试获取AAPL的历史数据
    symbol = 'AAPL'
    url = 'https://api.twelvedata.com/time_series'
    
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': 30,  # 获取30天数据测试
        'apikey': TWELVE_DATA_KEY,
        'format': 'JSON'
    }
    
    print(f"\n测试获取 {symbol} 最近30天数据...")
    print(f"请求URL: {url}")
    print(f"参数: {params}\n")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n返回数据:")
            print(f"状态: {data.get('status', 'N/A')}")
            print(f"元数据: {data.get('meta', {})}")
            
            values = data.get('values', [])
            print(f"\n数据点数量: {len(values)}")
            
            if values:
                print(f"\n最新3条数据:")
                for item in values[:3]:
                    print(f"  日期: {item['datetime']}, 收盘: {item['close']}, 成交量: {item['volume']}")
                
                print(f"\n✅ Twelve Data API 测试成功！")
                print(f"可以获取历史数据，数据质量良好")
            else:
                print(f"\n⚠️ 没有返回数据")
                if 'message' in data:
                    print(f"消息: {data['message']}")
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_twelve_data()
