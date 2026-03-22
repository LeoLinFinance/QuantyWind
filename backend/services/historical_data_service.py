"""
历史数据管理服务
- 存储市场指数和个股的历史数据
- 支持增量更新
- 只增不删的数据维护策略
- 使用Alpha Vantage API获取数据
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import time
from pathlib import Path

class HistoricalDataService:
    def __init__(self):
        # 数据存储路径
        self.data_dir = Path('data/historical')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / 'market_data.json'
        
        # Alpha Vantage API配置
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        if not self.alpha_vantage_key:
            print("⚠️ 警告: 未设置ALPHA_VANTAGE_API_KEY环境变量")
        
        # Twelve Data API配置
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY', '')
        if not self.twelve_data_key:
            print("⚠️ 警告: 未设置TWELVE_DATA_API_KEY环境变量")
        
        # API请求间隔
        self.alpha_vantage_delay = 12  # Alpha Vantage: 5次/分钟
        self.twelve_data_delay = 8  # Twelve Data: 8次/分钟（免费版）
        
        # 加载现有数据
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """加载历史数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载历史数据失败: {e}")
                return self._init_data_structure()
        return self._init_data_structure()
    
    def reload_data(self):
        """重新加载数据（公开方法）"""
        self.data = self._load_data()
    
    def _init_data_structure(self) -> Dict:
        """初始化数据结构"""
        return {
            'indices': {
                '^IXIC': {'symbol': '^IXIC', 'name': 'NASDAQ', 'data': [], 'last_update': None},
                '^GSPC': {'symbol': '^GSPC', 'name': 'S&P 500', 'data': [], 'last_update': None},
                '^RUT': {'symbol': '^RUT', 'name': 'Russell 2000', 'data': [], 'last_update': None},
            },
            'stocks': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_full_update': None,
            }
        }
    
    def _save_data(self):
        """保存数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史数据失败: {e}")
    
    def _fetch_from_twelve_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        从Twelve Data获取历史数据
        
        免费版限制：8次/分钟，800次/天
        数据覆盖：最多8年历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            历史数据列表
        """
        if not self.twelve_data_key:
            return []
        
        try:
            print(f"📥 正在从Twelve Data获取 {symbol} 的历史数据...")
            
            # Twelve Data使用不同的指数符号格式
            # 免费版只支持ETF，不支持直接的指数符号
            twelve_symbol = symbol
            if symbol.startswith('^'):
                symbol_map = {
                    '^IXIC': 'COMP',  # NASDAQ Composite
                    '^GSPC': 'SPY',   # S&P 500 ETF (免费版不支持SPX)
                    '^RUT': 'IWM',    # Russell 2000 ETF (免费版不支持RUT)
                }
                twelve_symbol = symbol_map.get(symbol, symbol[1:])  # 移除^前缀
                print(f"  转换指数符号: {symbol} -> {twelve_symbol}")
            
            url = 'https://api.twelvedata.com/time_series'
            params = {
                'symbol': twelve_symbol,
                'interval': '1day',
                'start_date': start_date,
                'end_date': end_date,
                'apikey': self.twelve_data_key,
                'format': 'JSON'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ {symbol} HTTP错误: {response.status_code}")
                return []
            
            data = response.json()
            
            # 检查错误
            if 'status' in data and data['status'] == 'error':
                print(f"❌ {symbol} API错误: {data.get('message', 'Unknown error')}")
                return []
            
            # 获取时间序列数据
            values = data.get('values', [])
            
            if not values:
                print(f"⚠️ {symbol} 没有返回数据")
                return []
            
            # 转换为标准格式
            history = []
            for item in values:
                try:
                    history.append({
                        'date': item['datetime'],
                        'open': float(item['open']),
                        'high': float(item['high']),
                        'low': float(item['low']),
                        'close': float(item['close']),
                        'volume': int(item['volume']),
                    })
                except (KeyError, ValueError) as e:
                    print(f"⚠️ 跳过无效数据: {item.get('datetime', 'unknown')}, 错误: {e}")
                    continue
            
            # 按日期排序（从旧到新）
            history.sort(key=lambda x: x['date'])
            
            if history:
                print(f"✅ {symbol} 从Twelve Data成功获取 {len(history)} 条数据")
            
            # API限流保护
            print(f"⏳ 等待{self.twelve_data_delay}秒（API限流保护）...")
            time.sleep(self.twelve_data_delay)
            
            return history
            
        except Exception as e:
            print(f"❌ {symbol} 从Twelve Data获取失败: {type(e).__name__}: {e}")
            return []
    
    def _fetch_yahoo_history(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        多源数据获取策略：
        1. 优先使用Twelve Data（8年历史数据）
        2. 如果失败，回退到Alpha Vantage（100天数据）
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            历史数据列表
        """
        # 策略1: 尝试Twelve Data
        if self.twelve_data_key:
            print(f"🔄 策略1: 尝试从Twelve Data获取数据...")
            data = self._fetch_from_twelve_data(symbol, start_date, end_date)
            if data:
                return data
            print(f"⚠️ Twelve Data获取失败，尝试备用方案...")
        
        # 策略2: 回退到Alpha Vantage
        if self.alpha_vantage_key:
            print(f"🔄 策略2: 尝试从Alpha Vantage获取数据...")
            data = self._fetch_from_alpha_vantage(symbol, start_date, end_date)
            if data:
                return data
        
        print(f"❌ 所有数据源都失败了")
        return []
    
    def _fetch_from_alpha_vantage(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        从Alpha Vantage获取历史数据
        
        注意：免费版只能获取最近100天的数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            历史数据列表
        """
        if not self.alpha_vantage_key:
            print(f"❌ {symbol} 无法获取数据：未设置API key")
            return []
        
        try:
            print(f"📥 正在从Alpha Vantage获取 {symbol} 的历史数据...")
            print(f"⚠️ 注意：免费版只能获取最近100天的数据")
            
            # Alpha Vantage API
            url = 'https://www.alphavantage.co/query'
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': 'compact',  # 免费版只支持compact（100天）
                'apikey': self.alpha_vantage_key,
                'datatype': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ {symbol} HTTP错误: {response.status_code}")
                return []
            
            data = response.json()
            
            # 检查错误信息
            if 'Error Message' in data:
                print(f"❌ {symbol} API错误: {data['Error Message']}")
                return []
            
            if 'Note' in data:
                print(f"⚠️ {symbol} API限流: {data['Note']}")
                print("请等待1分钟后重试")
                return []
            
            if 'Information' in data:
                print(f"ℹ️ {symbol} API信息: {data['Information']}")
                # 如果是付费功能提示，继续尝试获取compact数据
                if 'premium' in data['Information'].lower():
                    print(f"⚠️ 免费版限制：只能获取最近100天数据")
            
            # 获取时间序列数据
            time_series = data.get('Time Series (Daily)', {})
            
            if not time_series:
                print(f"⚠️ {symbol} 没有返回数据")
                return []
            
            # 转换为列表格式并过滤日期范围
            history = []
            for date_str, values in time_series.items():
                # 只保留指定日期范围内的数据
                if start_date <= date_str <= end_date:
                    try:
                        history.append({
                            'date': date_str,
                            'open': float(values['1. open']),
                            'high': float(values['2. high']),
                            'low': float(values['3. low']),
                            'close': float(values['4. close']),
                            'volume': int(values['5. volume']),
                        })
                    except (KeyError, ValueError) as e:
                        print(f"⚠️ 跳过无效数据: {date_str}, 错误: {e}")
                        continue
            
            # 按日期排序（从旧到新）
            history.sort(key=lambda x: x['date'])
            
            if history:
                print(f"✅ {symbol} 成功获取 {len(history)} 条数据 (日期范围: {history[0]['date']} 到 {history[-1]['date']})")
            else:
                print(f"⚠️ {symbol} 过滤后没有数据（请求范围: {start_date} 到 {end_date}）")
            
            # API限流保护：每次请求后等待
            print(f"⏳ 等待{self.alpha_vantage_delay}秒（API限流保护）...")
            time.sleep(self.alpha_vantage_delay)
            
            return history
            
        except requests.exceptions.Timeout:
            print(f"❌ {symbol} 请求超时")
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ {symbol} 网络请求失败: {e}")
            return []
        except Exception as e:
            print(f"❌ {symbol} 获取历史数据失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_last_update_date(self, symbol: str, is_index: bool = False) -> Optional[str]:
        """获取某个标的的最后更新日期"""
        category = 'indices' if is_index else 'stocks'
        
        if symbol in self.data[category]:
            data_list = self.data[category][symbol].get('data', [])
            if data_list:
                return data_list[-1]['date']
        
        return None
    
    def update_symbol_data(self, symbol: str, name: str, is_index: bool = False, 
                          start_date: Optional[str] = None) -> bool:
        """
        更新单个标的的数据（增量更新）
        
        Args:
            symbol: 股票代码
            name: 股票名称
            is_index: 是否是指数
            start_date: 开始日期（如果为None，则从最后更新日期开始）
        
        Returns:
            是否更新成功
        """
        category = 'indices' if is_index else 'stocks'
        
        # 确保标的存在于数据结构中
        if symbol not in self.data[category]:
            self.data[category][symbol] = {
                'symbol': symbol,
                'name': name,
                'data': [],
                'last_update': None,
                'is_active': True,
            }
        
        # 确定开始日期
        if start_date is None:
            last_date = self.get_last_update_date(symbol, is_index)
            if last_date:
                # 从最后更新日期的下一天开始
                last_dt = datetime.strptime(last_date, '%Y-%m-%d')
                start_date = (last_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                # 如果没有历史数据，尝试获取更长时间的数据
                # Twelve Data免费版支持8年，Alpha Vantage免费版只支持100天
                if self.twelve_data_key:
                    # 尝试获取5年数据
                    start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
                    print(f"📊 {symbol} 首次获取，尝试获取5年历史数据（Twelve Data）")
                else:
                    # 只能获取100天
                    start_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
                    print(f"📊 {symbol} 首次获取，只能获取100天数据（Alpha Vantage限制）")
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 如果开始日期晚于或等于结束日期，说明数据已是最新
        if start_date >= end_date:
            print(f"✅ {symbol} 数据已是最新")
            return True
        
        print(f"📥 更新 {symbol} 从 {start_date} 到 {end_date}")
        
        # 获取新数据
        new_data = self._fetch_yahoo_history(symbol, start_date, end_date)
        
        if new_data and len(new_data) > 0:
            # 追加新数据
            self.data[category][symbol]['data'].extend(new_data)
            self.data[category][symbol]['last_update'] = datetime.now().isoformat()
            self.data[category][symbol]['is_active'] = True
            
            # 保存数据
            self._save_data()
            print(f"✅ {symbol} 更新了 {len(new_data)} 条数据")
            return True
        else:
            print(f"❌ {symbol} 未能获取到数据")
            return False
    
    def update_all_active_symbols(self, watchlist_symbols: List[str]) -> Dict:
        """
        更新所有活跃的标的（指数 + 盯盘股票）
        
        Args:
            watchlist_symbols: 当前盯盘的股票列表
        
        Returns:
            更新统计信息
        """
        stats = {
            'updated': [],
            'failed': [],
            'skipped': [],
        }
        
        print(f"\n{'='*60}")
        print(f"开始更新历史数据")
        print(f"盯盘股票: {watchlist_symbols}")
        print(f"{'='*60}\n")
        
        # 更新指数
        print("📊 更新市场指数...")
        for symbol in self.data['indices'].keys():
            try:
                print(f"\n处理指数: {symbol}")
                if self.update_symbol_data(symbol, self.data['indices'][symbol]['name'], is_index=True):
                    stats['updated'].append(symbol)
                else:
                    stats['failed'].append(symbol)
            except Exception as e:
                print(f"❌ 更新{symbol}异常: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                stats['failed'].append(symbol)
        
        # 更新盯盘股票
        print(f"\n📈 更新盯盘股票...")
        for symbol in watchlist_symbols:
            try:
                print(f"\n处理股票: {symbol}")
                # 标记为活跃
                if symbol in self.data['stocks']:
                    self.data['stocks'][symbol]['is_active'] = True
                
                if self.update_symbol_data(symbol, symbol, is_index=False):
                    stats['updated'].append(symbol)
                else:
                    stats['failed'].append(symbol)
            except Exception as e:
                print(f"❌ 更新{symbol}异常: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                stats['failed'].append(symbol)
        
        # 标记不在盯盘中的股票为非活跃（但保留数据）
        for symbol in self.data['stocks'].keys():
            if symbol not in watchlist_symbols:
                self.data['stocks'][symbol]['is_active'] = False
        
        # 更新元数据
        self.data['metadata']['last_full_update'] = datetime.now().isoformat()
        self._save_data()
        
        print(f"\n{'='*60}")
        print(f"更新完成!")
        print(f"成功: {len(stats['updated'])} 个 - {stats['updated']}")
        print(f"失败: {len(stats['failed'])} 个 - {stats['failed']}")
        print(f"{'='*60}\n")
        
        return stats
    
    def get_symbol_data(self, symbol: str, is_index: bool = False, 
                       start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[Dict]:
        """
        获取某个标的的历史数据
        
        Args:
            symbol: 股票代码
            is_index: 是否是指数
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
        
        Returns:
            历史数据列表
        """
        category = 'indices' if is_index else 'stocks'
        
        if symbol not in self.data[category]:
            return []
        
        data = self.data[category][symbol].get('data', [])
        
        # 过滤日期范围
        if start_date or end_date:
            filtered_data = []
            for item in data:
                if start_date and item['date'] < start_date:
                    continue
                if end_date and item['date'] > end_date:
                    continue
                filtered_data.append(item)
            return filtered_data
        
        return data
    
    def get_all_symbols_data(self) -> Dict:
        """获取所有标的的数据摘要"""
        summary = {
            'indices': {},
            'stocks': {},
            'metadata': self.data['metadata'],
        }
        
        # 指数摘要
        for symbol, info in self.data['indices'].items():
            summary['indices'][symbol] = {
                'symbol': symbol,
                'name': info['name'],
                'data_points': len(info.get('data', [])),
                'last_update': info.get('last_update'),
                'date_range': self._get_date_range(info.get('data', [])),
            }
        
        # 股票摘要
        for symbol, info in self.data['stocks'].items():
            summary['stocks'][symbol] = {
                'symbol': symbol,
                'name': info['name'],
                'data_points': len(info.get('data', [])),
                'last_update': info.get('last_update'),
                'is_active': info.get('is_active', False),
                'date_range': self._get_date_range(info.get('data', [])),
            }
        
        return summary
    
    def _get_date_range(self, data: List[Dict]) -> Dict:
        """获取数据的日期范围"""
        if not data:
            return {'start': None, 'end': None}
        
        return {
            'start': data[0]['date'],
            'end': data[-1]['date'],
        }
    
    def get_statistics(self) -> Dict:
        """获取数据集统计信息"""
        total_indices = len(self.data['indices'])
        total_stocks = len(self.data['stocks'])
        active_stocks = sum(1 for s in self.data['stocks'].values() if s.get('is_active', False))
        
        total_data_points = 0
        for info in self.data['indices'].values():
            total_data_points += len(info.get('data', []))
        for info in self.data['stocks'].values():
            total_data_points += len(info.get('data', []))
        
        return {
            'total_indices': total_indices,
            'total_stocks': total_stocks,
            'active_stocks': active_stocks,
            'inactive_stocks': total_stocks - active_stocks,
            'total_data_points': total_data_points,
            'last_full_update': self.data['metadata'].get('last_full_update'),
            'created_at': self.data['metadata'].get('created_at'),
        }
