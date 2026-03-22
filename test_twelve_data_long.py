"""测试Twelve Data API获取长期历史数据"""
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_API_KEY')

def test_long_history():
    """测试获取长期历史数据"""
    symbol = 'AAPL'
    
    # 测试获取5年数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
    
    url = 'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': '1day',
        'start_date': start_date,
        'end_date': end_date,
        'apikey': TWELVE_DATA_KEY,
        'format': 'JSON'
    }
    
    print(f"测试获取 {symbol} 从 {start_date} 到 {end_date} 的数据...")
    print(f"预期约 {365*5} 个交易日数据\n")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'ok':
                values = data.get('values', [])
                print(f"✅ 成功获取 {len(values)} 条数据")
                
                if values:
                    print(f"\n最早数据: {values[-1]['datetime']}, 收盘: {values[-1]['close']}")
                    print(f"最新数据: {values[0]['datetime']}, 收盘: {values[0]['close']}")
                    print(f"\n🎉 Twelve Data可以获取长期历史数据！")
            else:
                print(f"❌ API返回错误")
                print(f"消息: {data.get('message', 'Unknown error')}")
                print(f"完整响应: {data}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == '__main__':
    test_long_history()
