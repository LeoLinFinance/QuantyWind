import requests
from typing import Dict, List, Optional
from datetime import datetime
import random

class YahooFinanceAPI:
    """Yahoo Finance API 封装（使用公开API）"""
    
    def __init__(self):
        self.base_url = 'https://query1.finance.yahoo.com/v8/finance/chart'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """获取股票实时报价"""
        try:
            url = f'{self.base_url}/{symbol}'
            params = {
                'interval': '1d',
                'range': '10d'  # 获取更多天数以确保有足够的数据
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"获取 {symbol} 失败: HTTP {response.status_code}")
                return self._get_mock_quote(symbol)
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                print(f"获取 {symbol} 数据格式错误")
                return self._get_mock_quote(symbol)
            
            result = data['chart']['result'][0]
            meta = result['meta']
            
            # 获取历史数据
            quotes = result.get('indicators', {}).get('quote', [{}])[0]
            closes = quotes.get('close', [])
            volumes = quotes.get('volume', [])
            opens = quotes.get('open', [])
            highs = quotes.get('high', [])
            lows = quotes.get('low', [])
            timestamps = result.get('timestamp', [])
            
            # 过滤掉None值，获取有效的收盘价
            valid_closes = [c for c in closes if c is not None]
            valid_volumes = [v for v in volumes if v is not None]
            
            if len(valid_closes) < 2:
                print(f"获取 {symbol} 历史数据不足")
                return self._get_mock_quote(symbol)
            
            # 使用meta中的实时价格和历史数据中的前收盘价
            # regularMarketPrice是当前实时价格
            # valid_closes[-2]是前一交易日的收盘价
            current_price = meta.get('regularMarketPrice', valid_closes[-1])
            
            # 前收盘价：优先使用chartPreviousClose，否则使用倒数第二个历史收盘价
            previous_close = meta.get('chartPreviousClose')
            if previous_close is None or previous_close == current_price:
                # 如果chartPreviousClose不可用或等于当前价格，使用倒数第二个历史收盘价
                previous_close = valid_closes[-2]
            
            change = current_price - previous_close
            change_percent = ((change / previous_close) * 100) if previous_close else 0
            change = current_price - previous_close
            change_percent = ((change / previous_close) * 100) if previous_close else 0
            
            # 获取最新的非空值
            volume = valid_volumes[-1] if valid_volumes else 0
            open_price = next((o for o in reversed(opens) if o is not None), current_price)
            high_price = next((h for h in reversed(highs) if h is not None), current_price)
            low_price = next((l for l in reversed(lows) if l is not None), current_price)
            
            # 获取一周成交量数据（最近7个交易日）
            volume_history = valid_volumes[-7:] if len(valid_volumes) >= 7 else valid_volumes
            
            return {
                'symbol': symbol,
                'name': meta.get('shortName', meta.get('longName', symbol)),
                'price': current_price,
                'change': change,
                'changePercent': change_percent,
                'volume': int(volume) if volume else 0,
                'volumeHistory': [int(v) for v in volume_history],  # 一周成交量历史
                'marketCap': 0,
                'previousClose': previous_close,
                'open': open_price,
                'dayHigh': high_price,
                'dayLow': low_price,
            }
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
            return self._get_mock_quote(symbol)
    
    def _get_mock_quote(self, symbol: str) -> Dict:
        """生成模拟股票数据"""
        mock_prices = {
            'AAPL': 178.50,
            'MSFT': 412.30,
            'TSLA': 234.80,
            'GOOGL': 145.60,
            'AMZN': 178.90,
            'NVDA': 875.20,
            'META': 485.30,
            'NFLX': 598.40,
            'AMD': 185.70,
            'INTC': 43.20
        }
        
        mock_names = {
            'AAPL': '苹果',
            'MSFT': '微软',
            'TSLA': '特斯拉',
            'GOOGL': '谷歌',
            'AMZN': '亚马逊',
            'NVDA': '英伟达',
            'META': 'Meta',
            'NFLX': '奈飞',
            'AMD': '超微半导体',
            'INTC': '英特尔'
        }
        
        base_price = mock_prices.get(symbol, 100.0)
        price = base_price + random.uniform(-5, 5)
        change_percent = random.uniform(-3, 3)
        change = price * change_percent / 100
        
        # 生成模拟的一周成交量数据
        base_volume = random.randint(10000000, 100000000)
        volume_history = [int(base_volume * random.uniform(0.7, 1.3)) for _ in range(7)]
        
        return {
            'symbol': symbol,
            'name': mock_names.get(symbol, symbol),
            'price': price,
            'change': change,
            'changePercent': change_percent,
            'volume': volume_history[-1],
            'volumeHistory': volume_history,
            'marketCap': 0,
            'previousClose': price - change,
            'open': price + random.uniform(-2, 2),
            'dayHigh': price + random.uniform(0, 3),
            'dayLow': price - random.uniform(0, 3),
        }
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[Dict]:
        """批量获取股票报价"""
        results = []
        for symbol in symbols:
            quote = self.get_stock_quote(symbol)
            if quote:
                results.append(quote)
        return results
    
    def search_stock(self, query: str) -> List[Dict]:
        """搜索股票"""
        try:
            # 尝试直接获取股票信息
            quote = self.get_stock_quote(query.upper())
            if quote and quote['price'] > 0:
                return [{
                    'symbol': quote['symbol'],
                    'name': quote['name'],
                    'exchange': 'US Market'
                }]
        except:
            pass
        
        # 如果失败，返回查询本身让用户尝试
        return [{
            'symbol': query.upper(),
            'name': query.upper(),
            'exchange': 'US Market'
        }]
    
    def get_index_data(self) -> Dict:
        """获取主要指数数据"""
        indices = {
            'nasdaq': '^IXIC',
            'sp500': '^GSPC',
            'russell': '^RUT'
        }
        
        result = {}
        for name, symbol in indices.items():
            try:
                url = f'{self.base_url}/{symbol}'
                params = {
                    'interval': '1d',
                    'range': '10d'
                }
                
                response = requests.get(url, params=params, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"获取指数 {name} 失败: HTTP {response.status_code}")
                    result[name] = {'value': 0, 'change': 0, 'changePercent': 0}
                    continue
                
                data = response.json()
                
                if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                    print(f"获取指数 {name} 数据格式错误")
                    result[name] = {'value': 0, 'change': 0, 'changePercent': 0}
                    continue
                
                # 获取历史收盘价
                quotes = data['chart']['result'][0]['indicators']['quote'][0]
                closes = quotes.get('close', [])
                valid_closes = [c for c in closes if c is not None]
                
                if len(valid_closes) < 2:
                    print(f"获取指数 {name} 历史数据不足")
                    result[name] = {'value': 0, 'change': 0, 'changePercent': 0}
                    continue
                
                # 使用最近两个交易日的收盘价计算涨跌幅
                current = valid_closes[-1]
                previous = valid_closes[-2]
                
                result[name] = {
                    'value': current,
                    'change': current - previous,
                    'changePercent': ((current - previous) / previous * 100) if previous else 0
                }
            except Exception as e:
                print(f"获取指数 {name} 失败: {e}")
                result[name] = {'value': 0, 'change': 0, 'changePercent': 0}
        
        return result
    
    def _get_mock_index(self, base_value: float) -> Dict:
        """生成模拟指数数据"""
        value = base_value + random.uniform(-100, 100)
        change_percent = random.uniform(-2, 2)
        change = value * change_percent / 100
        
        return {
            'value': value,
            'change': change,
            'changePercent': change_percent
        }
