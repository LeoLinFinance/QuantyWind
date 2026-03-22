from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .yahoo_finance_api import YahooFinanceAPI
from .ai_service import AIService
from .historical_data_service import HistoricalDataService
from .persistence_service import PersistenceService

class MarketService:
    def __init__(self):
        self.yahoo_api = YahooFinanceAPI()
        self.ai_service = AIService()
        self.historical_service = HistoricalDataService()
        self.persistence = PersistenceService()
        
        # 缓存机制
        self._market_insight_cache = None
        self._market_insight_cache_time = None
        self._watchlist_cache = {}  # {use_ai: {data: [], timestamp: datetime}}
        self._sentiment_cache = {}  # {symbol: {sentiment: str, timestamp: datetime}}
        
        # 从持久化存储加载盯盘列表
        saved_watchlist = self.persistence.load_watchlist()
        if saved_watchlist:
            self.watchlist_symbols = saved_watchlist
            print(f"✅ 从持久化存储加载了 {len(saved_watchlist)} 只股票")
        else:
            # 默认盯盘列表（仅在没有保存数据时使用）
            self.watchlist_symbols = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
            # 保存默认列表
            self.persistence.save_watchlist(self.watchlist_symbols)
            print(f"✅ 初始化默认盯盘列表: {len(self.watchlist_symbols)} 只股票")
        
        # 从持久化存储加载系统提示词
        self.system_prompt = self.persistence.load_system_prompt()
    
    def get_latest_insight(self, force_refresh: bool = False):
        """
        获取最新市场洞察
        
        Args:
            force_refresh: 是否强制刷新缓存（默认False）
        
        缓存策略：
        - 缓存有效期：5分钟
        - 只有缓存过期或force_refresh=True时才重新获取数据
        """
        # 检查缓存
        if not force_refresh and self._market_insight_cache and self._market_insight_cache_time:
            cache_age = datetime.now() - self._market_insight_cache_time
            if cache_age < timedelta(minutes=5):
                print(f"✅ 使用市场洞察缓存（缓存年龄: {cache_age.seconds}秒）")
                return self._market_insight_cache
        
        # 获取指数数据
        print("🔄 刷新市场洞察数据...")
        indices_data = self.yahoo_api.get_index_data()
        
        # 简单的市场情绪判断
        sp500_change = indices_data.get('sp500', {}).get('changePercent', 0)
        if sp500_change > 1:
            sentiment = '乐观'
            analysis = '市场整体表现强劲，主要指数全线上涨，投资者情绪积极。'
        elif sp500_change < -1:
            sentiment = '谨慎'
            analysis = '市场承压下行，投资者保持谨慎态度，关注风险控制。'
        else:
            sentiment = '中性'
            analysis = '市场窄幅震荡，投资者观望情绪浓厚，等待方向明朗。'
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'sentiment': sentiment,
            'analysis': analysis,
            'indices': {
                'nasdaq': indices_data.get('nasdaq', {}).get('value', 0),
                'sp500': indices_data.get('sp500', {}).get('value', 0),
                'russell': indices_data.get('russell', {}).get('value', 0),
                'nasdaq_change': indices_data.get('nasdaq', {}).get('changePercent', 0),
                'sp500_change': indices_data.get('sp500', {}).get('changePercent', 0),
                'russell_change': indices_data.get('russell', {}).get('changePercent', 0),
            }
        }
        
        # 更新缓存
        self._market_insight_cache = result
        self._market_insight_cache_time = datetime.now()
        
        return result
    
    def get_watchlist(self, use_ai: bool = True, force_refresh: bool = False):
        """
        获取盯盘股票列表
        
        Args:
            use_ai: 是否使用AI分析舆情
            force_refresh: 是否强制刷新缓存（默认False）
        
        缓存策略：
        - 基础数据（价格、涨跌幅）：实时获取（不缓存）
        - AI舆情分析：缓存15分钟
        """
        # 检查watchlist缓存（仅用于非强制刷新）
        cache_key = 'with_ai' if use_ai else 'without_ai'
        if not force_refresh and cache_key in self._watchlist_cache:
            cache_data = self._watchlist_cache[cache_key]
            cache_age = datetime.now() - cache_data['timestamp']
            
            # 如果不使用AI，缓存1分钟；使用AI时缓存15分钟
            cache_duration = timedelta(minutes=15 if use_ai else 1)
            
            if cache_age < cache_duration:
                print(f"✅ 使用盯盘列表缓存（use_ai={use_ai}, 缓存年龄: {cache_age.seconds}秒）")
                return cache_data['data']
        
        # 获取股票基础数据（价格、涨跌幅等）
        print(f"🔄 刷新盯盘列表数据（use_ai={use_ai}）...")
        stocks = self.yahoo_api.get_multiple_quotes(self.watchlist_symbols)
        
        if use_ai and stocks:
            # 检查每只股票的舆情缓存
            need_ai_analysis = []
            for stock in stocks:
                symbol = stock['symbol']
                if symbol in self._sentiment_cache:
                    cache_age = datetime.now() - self._sentiment_cache[symbol]['timestamp']
                    if cache_age < timedelta(minutes=15):
                        # 使用缓存的舆情
                        stock['sentiment'] = self._sentiment_cache[symbol]['sentiment']
                        print(f"✅ 使用 {symbol} 舆情缓存（缓存年龄: {cache_age.seconds}秒）")
                    else:
                        need_ai_analysis.append(stock)
                else:
                    need_ai_analysis.append(stock)
            
            # 只对需要更新的股票进行AI分析
            if need_ai_analysis:
                print(f"🤖 对 {len(need_ai_analysis)} 只股票进行AI舆情分析...")
                sentiments = self.ai_service.batch_analyze_sentiment(
                    need_ai_analysis, 
                    system_prompt=self.system_prompt
                )
                
                # 更新舆情缓存
                for stock in need_ai_analysis:
                    symbol = stock['symbol']
                    sentiment = sentiments.get(symbol, '暂无舆情数据')
                    stock['sentiment'] = sentiment
                    self._sentiment_cache[symbol] = {
                        'sentiment': sentiment,
                        'timestamp': datetime.now()
                    }
        else:
            # 不使用AI时返回空舆情
            for stock in stocks:
                stock['sentiment'] = '暂无舆情数据'
        
        # 更新watchlist缓存
        self._watchlist_cache[cache_key] = {
            'data': stocks,
            'timestamp': datetime.now()
        }
        
        return stocks
    
    def add_stock(self, symbol: str) -> Dict:
        """
        添加股票到盯盘列表
        自动触发历史数据获取
        """
        symbol = symbol.upper()
        if symbol in self.watchlist_symbols:
            return {'success': False, 'message': '股票已在盯盘列表中'}
        
        # 验证股票是否存在
        quote = self.yahoo_api.get_stock_quote(symbol)
        if quote:
            self.watchlist_symbols.append(symbol)
            
            # 保存到持久化存储
            self.persistence.save_watchlist(self.watchlist_symbols)
            
            # 自动获取历史数据（异步执行，不阻塞响应）
            try:
                print(f"📥 自动获取 {symbol} 的历史数据...")
                self.historical_service.update_symbol_data(
                    symbol=symbol,
                    name=quote['name'],
                    is_index=False
                )
                print(f"✅ {symbol} 历史数据获取完成")
            except Exception as e:
                print(f"⚠️ {symbol} 历史数据获取失败: {e}")
                # 不影响添加操作
            
            return {
                'success': True, 
                'symbol': symbol, 
                'name': quote['name'],
                'message': f'{symbol} 已添加到盯盘列表，历史数据正在后台获取'
            }
        else:
            return {'success': False, 'message': '未找到该股票'}
    
    def remove_stock(self, symbol: str) -> Dict:
        """
        从盯盘列表移除股票
        数据集中标记为非活跃，但保留历史数据
        """
        symbol = symbol.upper()
        if symbol in self.watchlist_symbols:
            self.watchlist_symbols.remove(symbol)
            
            # 保存到持久化存储
            self.persistence.save_watchlist(self.watchlist_symbols)
            
            # 标记为非活跃（数据保留但不再更新）
            try:
                if symbol in self.historical_service.data['stocks']:
                    self.historical_service.data['stocks'][symbol]['is_active'] = False
                    self.historical_service._save_data()
                    print(f"📝 {symbol} 已标记为非活跃，历史数据已保留")
            except Exception as e:
                print(f"⚠️ 标记 {symbol} 为非活跃失败: {e}")
            
            return {
                'success': True, 
                'symbol': symbol,
                'message': f'{symbol} 已从盯盘列表移除，历史数据已保留'
            }
        return {'success': False, 'message': '股票不在盯盘列表中'}
    
    def get_single_stock(self, symbol: str) -> Optional[Dict]:
        """
        获取单只股票的数据（不含AI舆情）
        用于添加股票时只获取新股票的数据，避免影响其他股票
        """
        symbol = symbol.upper()
        quote = self.yahoo_api.get_stock_quote(symbol)
        if quote:
            quote['sentiment'] = '暂无舆情数据'
        return quote
    
    def search_stock(self, query: str) -> List[Dict]:
        """搜索股票"""
        return self.yahoo_api.search_stock(query)
    
    def update_system_prompt(self, prompt: str) -> Dict:
        """更新AI系统提示词"""
        self.system_prompt = prompt
        # 保存到持久化存储
        self.persistence.save_system_prompt(prompt)
        return {'success': True, 'prompt': prompt}
    
    def get_system_prompt(self) -> Dict:
        """获取当前系统提示词"""
        default_prompt = """你是一个专业的美股市场分析师。请基于最新的市场动态和新闻，
为指定股票提供简短的舆情分析（不超过30字）。
重点关注：
1. 近期重大新闻事件
2. 市场情绪变化
3. 短期价格影响因素
请用简洁、专业的语言回答。"""
        return {'prompt': self.system_prompt or default_prompt}
