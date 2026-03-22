"""
新闻总结服务
使用StepFun API对新闻进行总结
"""
from openai import OpenAI
import logging
from typing import Dict, List
from datetime import datetime
from services.news_service import NewsService
from services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

class NewsSummaryService:
    """新闻总结服务"""
    
    def __init__(self):
        import os
        # 使用StepFun API - 资讯总结专用API Key
        self.client = OpenAI(
            api_key=os.getenv('STEPFUN_API_KEY', ''),
            base_url="https://api.stepfun.com/v1"
        )
        self.model = "step-1-32k"
        
        # 初始化其他服务
        self.news_service = NewsService()
        self.portfolio_service = PortfolioService()
        
        # 默认总结提示词
        self.default_summary_prompt = """你是一位专业的金融资讯分析师。请根据以下最新新闻资讯，为投资者提供一份简洁但全面的市场总结报告。

报告应包括：
1. 市场整体趋势和情绪
2. 重要的宏观经济事件和数据
3. 关键个股的重大新闻
4. 对投资组合的潜在影响
5. 需要关注的风险和机会

请用专业但易懂的语言，条理清晰地总结。"""
        
        logger.info("✅ News Summary Service initialized with StepFun API")
    
    def summarize_news(self, custom_prompt: str = None, last_time: str = None) -> Dict:
        """
        总结最新新闻资讯（使用与市场洞察相同的新闻数据源）
        
        Args:
            custom_prompt: 自定义总结提示词
            last_time: 上次获取新闻的时间
        
        Returns:
            总结结果字典
        """
        try:
            # 1. 获取持仓股票
            portfolio = self.portfolio_service.get_portfolio()
            holdings = portfolio.get('holdings', [])
            stock_symbols = [h['symbol'] for h in holdings]
            
            # 2. 获取市场新闻（与市场洞察舆情分析相同的数据源）
            logger.info("📰 获取市场新闻（使用NewsService）...")
            market_news = self.news_service.get_market_news(limit=10)
            
            # 3. 获取持仓股票的新闻（与市场洞察个股盯盘相同的数据源）
            portfolio_news = []
            for symbol in stock_symbols[:5]:  # 只获取前5只股票的新闻
                try:
                    stock_news = self.news_service.get_stock_news(symbol, limit=3)
                    portfolio_news.extend(stock_news)
                except Exception as e:
                    logger.warning(f"获取{symbol}新闻失败: {e}")
            
            # 4. 合并并去重新闻
            all_news = market_news + portfolio_news
            seen_titles = set()
            unique_news = []
            for news in all_news:
                title = news.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(news)
            
            # 按时间排序
            unique_news.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            logger.info(f"📊 获取到 {len(unique_news)} 条新闻（市场: {len(market_news)}, 持仓: {len(portfolio_news)}）")
            
            # 5. 格式化新闻为文本
            news_text = self._format_news_for_summary(unique_news[:15], stock_symbols)
            
            # 6. 使用StepFun API进行总结
            logger.info("🤖 使用StepFun API进行总结...")
            summary_prompt = custom_prompt or self.default_summary_prompt
            
            summary = self._call_stepfun_api(summary_prompt, news_text)
            
            return {
                'summary': summary,
                'news_count': len(unique_news),
                'portfolio_symbols': stock_symbols,
                'timestamp': datetime.now().isoformat(),
                'source': 'news_service_stepfun_summary',
                'news_sources': {
                    'market_news': len(market_news),
                    'portfolio_news': len(portfolio_news)
                }
            }
            
        except Exception as e:
            logger.error(f"新闻总结失败: {e}")
            return {
                'summary': f"新闻总结暂时不可用: {str(e)}",
                'news_count': 0,
                'portfolio_symbols': [],
                'timestamp': datetime.now().isoformat(),
                'source': 'error'
            }
    
    def _format_news_for_summary(self, news_list: List[Dict], portfolio_symbols: List[str]) -> str:
        """
        将新闻格式化为适合总结的文本
        
        Args:
            news_list: 新闻列表
            portfolio_symbols: 持仓股票代码
        
        Returns:
            格式化的新闻文本
        """
        if not news_list:
            return "暂无最新新闻。"
        
        formatted = f"【最新市场资讯汇总】\n"
        formatted += f"时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n"
        formatted += f"当前持仓: {', '.join(portfolio_symbols) if portfolio_symbols else '无'}\n\n"
        
        formatted += "=" * 60 + "\n\n"
        
        for i, news in enumerate(news_list, 1):
            # 计算时间差
            timestamp = news.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
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
                time_str = '最近'
            
            formatted += f"【新闻{i}】[{time_str}] {news.get('source', '未知来源')}\n"
            formatted += f"标题: {news.get('title', '无标题')}\n"
            
            if news.get('summary'):
                formatted += f"摘要: {news.get('summary', '')}\n"
            
            formatted += f"情绪: {news.get('sentiment', 'Neutral')}\n"
            formatted += "\n"
        
        formatted += "=" * 60 + "\n\n"
        formatted += "请基于以上新闻资讯，提供专业的市场分析和投资建议。"
        
        return formatted
    
    def _call_stepfun_api(self, system_prompt: str, news_text: str) -> str:
        """
        调用StepFun API进行总结
        
        Args:
            system_prompt: 系统提示词
            news_text: 新闻文本
        
        Returns:
            总结结果
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": news_text}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                tokens = response.usage.total_tokens if response.usage else 'N/A'
                logger.info(f"✅ StepFun总结成功: {len(content)} 字符, tokens: {tokens}")
                return content
            else:
                raise Exception("API返回空响应")
                
        except Exception as e:
            logger.error(f"❌ StepFun API调用失败: {type(e).__name__}: {e}")
            return f"新闻总结失败: {str(e)}"
    
    def get_default_prompt(self) -> str:
        """获取默认总结提示词"""
        return self.default_summary_prompt
    
    def update_default_prompt(self, new_prompt: str):
        """更新默认总结提示词"""
        self.default_summary_prompt = new_prompt
        logger.info("✅ 默认总结提示词已更新")
