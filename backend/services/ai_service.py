import os
import requests
from typing import Optional, Dict
import json
from .news_service import NewsService

class AIService:
    """AI模型服务 - 支持阶跃星辰和Kimi，集成实时新闻"""
    
    def __init__(self):
        # 阶跃星辰配置
        self.stepfun_api_key = os.getenv('STEPFUN_API_KEY', '')
        self.stepfun_url = 'https://api.stepfun.com/v1/chat/completions'
        # 使用Step 1v 8k模型（更经济的选择）
        self.stepfun_model = os.getenv('STEPFUN_MODEL', 'step-1v-8k')
        
        # Kimi配置
        self.kimi_api_key = os.getenv('KIMI_API_KEY', '')
        self.kimi_url = 'https://api.moonshot.cn/v1/chat/completions'
        
        # 新闻服务
        self.news_service = NewsService()
        
        # 默认使用阶跃星辰
        self.current_provider = 'stepfun'
        
        print(f"✅ AI服务初始化: 使用阶跃星辰模型 {self.stepfun_model}")
    
    def analyze_sentiment(self, 
                         stock_symbol: str, 
                         stock_name: str,
                         system_prompt: Optional[str] = None,
                         provider: str = 'stepfun',
                         include_news: bool = True) -> str:
        """
        分析股票舆情
        
        Args:
            stock_symbol: 股票代码
            stock_name: 股票名称
            system_prompt: 自定义系统提示词
            provider: AI提供商 ('stepfun' 或 'kimi')
            include_news: 是否包含实时新闻
        """
        if system_prompt is None:
            system_prompt = """你是一个专业的美股市场分析师。请基于提供的最新新闻和市场动态，
为指定股票提供简短的舆情分析（不超过30字）。
重点关注：
1. 近期重大新闻事件
2. 市场情绪变化
3. 短期价格影响因素
请用简洁、专业的语言回答。今天是2026年3月10日。"""
        
        # 获取实时新闻
        news_context = ""
        if include_news:
            try:
                news_list = self.news_service.get_stock_news(stock_symbol, limit=3)
                if news_list:
                    news_context = self.news_service.format_news_for_ai(news_list)
                else:
                    news_context = "暂无该股票的最新新闻。"
            except Exception as e:
                print(f"获取新闻失败: {e}")
                news_context = "新闻获取失败，基于一般市场情况分析。"
        
        user_prompt = f"""请分析 {stock_name}({stock_symbol}) 的当前舆情和短期影响。

{news_context}

请基于以上最新信息，用不超过30字简要分析该股票的舆情和短期影响。"""
        
        try:
            if provider == 'stepfun':
                return self._call_stepfun(system_prompt, user_prompt)
            elif provider == 'kimi':
                return self._call_kimi(system_prompt, user_prompt)
            else:
                return "不支持的AI提供商"
        except Exception as e:
            print(f"AI分析失败: {e}")
            return "暂无舆情数据"
    
    def _call_stepfun(self, system_prompt: str, user_prompt: str, max_tokens: int = 100, model: str = None) -> str:
        """
        调用阶跃星辰API
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_tokens: 最大token数
            model: 指定模型（如果为None则使用默认模型）
        """
        # 如果没有指定模型，使用默认的8k模型
        use_model = model if model else self.stepfun_model
        
        headers = {
            'Authorization': f'Bearer {self.stepfun_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': use_model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.7,
            'max_tokens': max_tokens
        }
        
        print(f"🤖 调用阶跃星辰API: 模型={use_model}, max_tokens={max_tokens}")
        
        try:
            response = requests.post(self.stepfun_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                print(f"✅ AI响应成功: {len(content)} 字符")
                return content
            else:
                error_msg = f"阶跃星辰API错误: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return f"AI分析暂时不可用 (错误码: {response.status_code})"
        except requests.exceptions.Timeout:
            print("❌ API请求超时")
            return "AI分析超时，请稍后重试"
        except Exception as e:
            print(f"❌ API调用异常: {type(e).__name__}: {e}")
            return f"AI分析失败: {str(e)}"
    
    def _call_kimi(self, system_prompt: str, user_prompt: str) -> str:
        """调用Kimi API"""
        headers = {
            'Authorization': f'Bearer {self.kimi_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'moonshot-v1-8k',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 100
        }
        
        response = requests.post(self.kimi_url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"Kimi API错误: {response.status_code} - {response.text}")
            return "AI分析暂时不可用"
    
    def batch_analyze_sentiment(self, 
                                stocks: list,
                                system_prompt: Optional[str] = None,
                                provider: str = 'stepfun') -> Dict[str, str]:
        """批量分析股票舆情"""
        results = {}
        for stock in stocks:
            symbol = stock.get('symbol')
            name = stock.get('name', symbol)
            sentiment = self.analyze_sentiment(symbol, name, system_prompt, provider)
            results[symbol] = sentiment
        return results
