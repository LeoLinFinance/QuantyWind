import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import feedparser

class NewsService:
    """实时新闻服务 - 使用免费的RSS源和公开API"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def get_stock_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """
        获取特定股票的最新新闻
        
        Args:
            symbol: 股票代码
            limit: 返回新闻数量
        
        Returns:
            新闻列表，每条新闻包含标题、摘要、时间等
        """
        news = []
        
        # 从Yahoo Finance RSS获取新闻
        try:
            yahoo_news = self._get_yahoo_finance_news(symbol, limit)
            news.extend(yahoo_news)
        except Exception as e:
            print(f"Yahoo Finance新闻获取失败: {e}")
        
        # 从Google Finance获取新闻
        if len(news) < limit:
            try:
                google_news = self._get_google_finance_news(symbol, limit - len(news))
                news.extend(google_news)
            except Exception as e:
                print(f"Google Finance新闻获取失败: {e}")
        
        # 按时间排序，最新的在前
        news.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return news[:limit]
    
    def _get_yahoo_finance_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """从Yahoo Finance RSS获取新闻"""
        try:
            # Yahoo Finance RSS feed
            rss_url = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US'
            
            feed = feedparser.parse(rss_url)
            news = []
            
            for entry in feed.entries[:limit]:
                # 解析发布时间
                try:
                    pub_date = entry.get('published_parsed')
                    if pub_date:
                        timestamp = int(datetime(*pub_date[:6]).timestamp())
                    else:
                        timestamp = int(datetime.now().timestamp())
                except:
                    timestamp = int(datetime.now().timestamp())
                
                # 提取摘要
                summary = entry.get('summary', '')
                if len(summary) > 200:
                    summary = summary[:200] + '...'
                
                news.append({
                    'title': entry.get('title', ''),
                    'summary': summary,
                    'source': 'Yahoo Finance',
                    'timestamp': timestamp,
                    'url': entry.get('link', ''),
                    'sentiment': self._analyze_headline_sentiment(entry.get('title', ''))
                })
            
            return news
        except Exception as e:
            print(f"Yahoo RSS解析失败: {e}")
            return []
    
    def _get_google_finance_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """从Google Finance获取新闻（通过RSS）"""
        try:
            # Google News RSS for finance
            rss_url = f'https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en'
            
            feed = feedparser.parse(rss_url)
            news = []
            
            for entry in feed.entries[:limit]:
                # 解析发布时间
                try:
                    pub_date = entry.get('published_parsed')
                    if pub_date:
                        timestamp = int(datetime(*pub_date[:6]).timestamp())
                    else:
                        timestamp = int(datetime.now().timestamp())
                except:
                    timestamp = int(datetime.now().timestamp())
                
                news.append({
                    'title': entry.get('title', ''),
                    'summary': '',
                    'source': 'Google News',
                    'timestamp': timestamp,
                    'url': entry.get('link', ''),
                    'sentiment': self._analyze_headline_sentiment(entry.get('title', ''))
                })
            
            return news
        except Exception as e:
            print(f"Google News解析失败: {e}")
            return []
    
    def _analyze_headline_sentiment(self, headline: str) -> str:
        """简单的标题情绪分析"""
        headline_lower = headline.lower()
        
        positive_words = ['surge', 'soar', 'gain', 'rise', 'jump', 'rally', 'beat', 'strong', 'growth', 
                         'profit', 'up', 'high', 'boost', 'win', 'success', 'positive', 'bullish']
        negative_words = ['fall', 'drop', 'plunge', 'decline', 'loss', 'weak', 'miss', 'cut', 'concern', 
                         'risk', 'down', 'low', 'crash', 'fail', 'negative', 'bearish', 'warning']
        
        positive_count = sum(1 for word in positive_words if word in headline_lower)
        negative_count = sum(1 for word in negative_words if word in headline_lower)
        
        if positive_count > negative_count:
            return 'Positive'
        elif negative_count > positive_count:
            return 'Negative'
        else:
            return 'Neutral'
    
    def get_market_news(self, limit: int = 10) -> List[Dict]:
        """获取整体市场新闻"""
        news = []
        
        # 获取主要指数和热门股票的新闻
        symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']
        for symbol in symbols:
            try:
                stock_news = self.get_stock_news(symbol, limit=2)
                news.extend(stock_news)
            except:
                pass
        
        # 去重并排序
        seen_titles = set()
        unique_news = []
        for item in news:
            title = item.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)
        
        unique_news.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return unique_news[:limit]
    
    def format_news_for_ai(self, news_list: List[Dict]) -> str:
        """将新闻格式化为AI可读的文本"""
        if not news_list:
            return "暂无最新新闻。"
        
        formatted = "最新市场新闻（2026年3月10日）：\n\n"
        
        for i, news in enumerate(news_list[:3], 1):  # 只取前3条
            timestamp = news.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                # 计算时间差
                time_diff = datetime.now() - dt
                if time_diff.days == 0:
                    if time_diff.seconds < 3600:
                        time_str = f"{time_diff.seconds // 60}分钟前"
                    else:
                        time_str = f"{time_diff.seconds // 3600}小时前"
                elif time_diff.days == 1:
                    time_str = "昨天"
                else:
                    time_str = f"{time_diff.days}天前"
            else:
                time_str = '未知时间'
            
            formatted += f"{i}. [{time_str}] {news.get('title', '无标题')}\n"
            if news.get('summary'):
                formatted += f"   {news.get('summary', '')}\n"
            formatted += f"   情绪倾向: {news.get('sentiment', 'Neutral')}\n\n"
        
        return formatted
