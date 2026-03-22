from datetime import datetime
from typing import List, Dict, Optional
from .news_service import NewsService
from .ai_service import AIService
import random

class SentimentService:
    def __init__(self):
        self.news_service = NewsService()
        self.ai_service = AIService()
        self.cache = {}
        self.cache_time = None
        self.default_system_prompt = """你是一个专业的金融风险分析师。请分析新闻并判断其风险等级和地理位置。

风险等级定义：

【高风险】（约占5-10%）- 符合以下任一条件：
1. 直接冲击全行业、全产业链、供应链、核心金融市场稳定
2. 具有跨市场、跨板块、跨区域传导性
3. 引发系统性、全局性、不可逆的经济冲击
4. 影响整个板块/整条产业链/一类金融资产
5. 引发股价崩盘、大宗商品暴涨暴跌、大面积违约、供应链停摆
6. 触发资本外流、融资冻结、行业信任崩塌
7. 全球/全国市场联动反应
例如：龙头企业财务造假暴雷、重大金融风险事件、关键原材料断供/制裁、行业级安全危机

【中风险】（约占20-30%）- 符合以下任一条件：
1. 影响单一公司、单一细分行业、产业链某一环节、局部市场
2. 造成阶段性、局部性、可修复的波动
3. 不形成系统性风险
4. 引发短期股价波动、局部供应紧张、阶段性信任质疑
5. 可通过澄清、整改、替换供应等方式化解
6. 无跨市场、跨区域大规模传导
例如：上市公司业绩暴雷、产品召回、产业链某环节短缺、区域性金融产品违约

【低风险】（约占60-70%）- 符合以下任一条件：
1. 仅涉及非核心主体、小众细分领域、非关键节点
2. 对股价、市场、供应链、消费无实质影响
3. 传播范围小、很快平息
4. 不影响价格、不影响供应、不影响融资
5. 无投资者恐慌、无产业链波动
6. 仅小范围讨论，不被主流财经媒体放大
例如：小众企业轻微负面、非关键零部件质疑、冷门细分品类争议

地理位置判断规则：
1. 如果新闻明确提到国家名称（如"美国"、"中国"、"Iran"等），请提取该国家
2. 如果新闻提到公司但未提国家，根据公司总部所在地判断（如Tesla→美国，Nvidia→美国）
3. 如果新闻涉及地缘政治、冲突、政策，请提取相关国家
4. 如果完全无法判断，返回null
5. 优先使用英文国家名称（如"United States"、"China"、"Iran"）

请以JSON格式回复，包含：
{
  "risk_level": "high/medium/low",
  "country": "国家英文名称（如United States、China、Iran）或null",
  "summary": "不超过50字的关键信息总结",
  "risk_details": "详细风险描述，包括具体风险点和影响范围（100-200字）",
  "affected_industries": ["受影响的产业/行业"],
  "related_stocks": ["相关股票代码"],
  "confidence": "high/medium/low（对地理位置判断的信心）"
}

今天是2026年3月10日。"""
    
    def get_map_data(self, custom_prompt: Optional[str] = None):
        """获取舆情地图数据"""
        # 检查缓存（1小时有效）
        cache_key = f"map_data_{hash(custom_prompt) if custom_prompt else 'default'}"
        if cache_key in self.cache and self.cache_time and (datetime.now() - self.cache_time).seconds < 3600:
            return self.cache[cache_key]
        
        # 获取市场新闻
        market_news = self.news_service.get_market_news(limit=20)
        
        # 使用AI分析新闻并分类
        analyzed_events = self._analyze_news_with_ai(market_news, custom_prompt)
        
        # 分离已定位和不确定地区的事件
        located_events = [e for e in analyzed_events if e.get('country')]
        uncertain_events = [e for e in analyzed_events if not e.get('country')]
        
        result = {
            'located': located_events,
            'uncertain': uncertain_events
        }
        
        # 更新缓存
        self.cache[cache_key] = result
        self.cache_time = datetime.now()
        
        return result
    
    def _analyze_news_with_ai(self, news_list: List[Dict], custom_prompt: Optional[str] = None) -> List[Dict]:
        """使用AI分析新闻并提取风险信息"""
        events = []

        system_prompt = custom_prompt if custom_prompt else self.default_system_prompt

        for news in news_list[:15]:  # 分析前15条新闻
            try:
                user_prompt = f"""请分析以下新闻的风险等级和地理位置：

    标题：{news.get('title', '')}
    摘要：{news.get('summary', '')}
    时间：{datetime.fromtimestamp(news.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M')}

    请判断：
    1. 风险等级（high/medium/low）
    2. 涉及的国家（如果能确定）
    3. 50字以内的关键信息总结
    4. 详细风险描述（100-200字）
    5. 受影响的产业/行业
    6. 相关的美股代码"""

                # 调用AI分析（使用更大的max_tokens以获取完整响应）
                response = self.ai_service._call_stepfun(system_prompt, user_prompt, max_tokens=500)

                # 解析AI响应
                import json
                try:
                    # 尝试提取JSON
                    if '{' in response and '}' in response:
                        json_start = response.index('{')
                        json_end = response.rindex('}') + 1
                        json_str = response[json_start:json_end]
                        analysis = json.loads(json_str)
                    else:
                        # 如果没有JSON，使用默认值
                        analysis = {
                            'risk_level': 'low',
                            'country': None,
                            'summary': news.get('title', '')[:50],
                            'risk_details': '',
                            'affected_industries': [],
                            'related_stocks': [],
                            'confidence': 'low'
                        }
                except:
                    analysis = {
                        'risk_level': 'low',
                        'country': None,
                        'summary': news.get('title', '')[:50],
                        'risk_details': '',
                        'affected_industries': [],
                        'related_stocks': [],
                        'confidence': 'low'
                    }

                # 构建事件对象
                event = {
                    'id': str(hash(news.get('title', '') + str(news.get('timestamp', 0)))),
                    'summary': analysis.get('summary', news.get('title', ''))[:50],
                    'riskDetails': analysis.get('risk_details', ''),
                    'affectedIndustries': analysis.get('affected_industries', []),
                    'timestamp': datetime.fromtimestamp(news.get('timestamp', 0)).isoformat(),
                    'riskLevel': analysis.get('risk_level', 'low'),
                    'relatedStocks': analysis.get('related_stocks', []),
                    'source': news.get('source', ''),
                    'url': news.get('url', '')
                }

                # 添加地理位置信息
                country = analysis.get('country')
                confidence = analysis.get('confidence', 'low')

                # 如果AI给出了国家信息，即使confidence是low也尝试使用
                if country and country.lower() not in ['null', 'none', 'unknown', '未知', '不确定']:
                    event['country'] = country
                    event['countryCode'] = self._get_country_code(country)
                    event['coordinates'] = self._get_country_coordinates(country)

                events.append(event)

            except Exception as e:
                print(f"AI分析新闻失败: {e}")
                # 添加默认事件
                events.append({
                    'id': str(hash(news.get('title', '') + str(news.get('timestamp', 0)))),
                    'summary': news.get('title', '')[:50],
                    'riskDetails': '',
                    'affectedIndustries': [],
                    'timestamp': datetime.fromtimestamp(news.get('timestamp', 0)).isoformat(),
                    'riskLevel': 'low',
                    'relatedStocks': [],
                    'source': news.get('source', ''),
                })

        return events
    
    def _get_country_code(self, country: str) -> str:
        """获取国家代码"""
        country_codes = {
            '美国': 'US', 'United States': 'US', 'USA': 'US', 'US': 'US',
            '中国': 'CN', 'China': 'CN', 'CN': 'CN',
            '日本': 'JP', 'Japan': 'JP', 'JP': 'JP',
            '德国': 'DE', 'Germany': 'DE', 'DE': 'DE',
            '英国': 'GB', 'UK': 'GB', 'United Kingdom': 'GB', 'GB': 'GB',
            '法国': 'FR', 'France': 'FR', 'FR': 'FR',
            '印度': 'IN', 'India': 'IN', 'IN': 'IN',
            '俄罗斯': 'RU', 'Russia': 'RU', 'RU': 'RU',
            '巴西': 'BR', 'Brazil': 'BR', 'BR': 'BR',
            '加拿大': 'CA', 'Canada': 'CA', 'CA': 'CA',
            '伊朗': 'IR', 'Iran': 'IR', 'IR': 'IR',
            '以色列': 'IL', 'Israel': 'IL', 'IL': 'IL',
            '沙特': 'SA', 'Saudi Arabia': 'SA', 'SA': 'SA',
            '韩国': 'KR', 'South Korea': 'KR', 'Korea': 'KR', 'KR': 'KR',
            '墨西哥': 'MX', 'Mexico': 'MX', 'MX': 'MX',
            '澳大利亚': 'AU', 'Australia': 'AU', 'AU': 'AU',
        }
        return country_codes.get(country, 'US')
    
    def _get_country_coordinates(self, country: str) -> List[float]:
        """获取国家坐标"""
        coordinates = {
            '美国': [-95.7129, 37.0902],
            'United States': [-95.7129, 37.0902],
            'USA': [-95.7129, 37.0902],
            'US': [-95.7129, 37.0902],
            '中国': [104.1954, 35.8617],
            'China': [104.1954, 35.8617],
            'CN': [104.1954, 35.8617],
            '日本': [138.2529, 36.2048],
            'Japan': [138.2529, 36.2048],
            'JP': [138.2529, 36.2048],
            '德国': [10.4515, 51.1657],
            'Germany': [10.4515, 51.1657],
            'DE': [10.4515, 51.1657],
            '英国': [-3.4360, 55.3781],
            'UK': [-3.4360, 55.3781],
            'United Kingdom': [-3.4360, 55.3781],
            'GB': [-3.4360, 55.3781],
            '法国': [2.2137, 46.2276],
            'France': [2.2137, 46.2276],
            'FR': [2.2137, 46.2276],
            '印度': [78.9629, 20.5937],
            'India': [78.9629, 20.5937],
            'IN': [78.9629, 20.5937],
            '俄罗斯': [105.3188, 61.5240],
            'Russia': [105.3188, 61.5240],
            'RU': [105.3188, 61.5240],
            '巴西': [-51.9253, -14.2350],
            'Brazil': [-51.9253, -14.2350],
            'BR': [-51.9253, -14.2350],
            '加拿大': [-106.3468, 56.1304],
            'Canada': [-106.3468, 56.1304],
            'CA': [-106.3468, 56.1304],
            '伊朗': [53.6880, 32.4279],
            'Iran': [53.6880, 32.4279],
            'IR': [53.6880, 32.4279],
            '以色列': [34.8516, 31.0461],
            'Israel': [34.8516, 31.0461],
            'IL': [34.8516, 31.0461],
            '沙特': [45.0792, 23.8859],
            'Saudi Arabia': [45.0792, 23.8859],
            'SA': [45.0792, 23.8859],
            '韩国': [127.7669, 35.9078],
            'South Korea': [127.7669, 35.9078],
            'Korea': [127.7669, 35.9078],
            'KR': [127.7669, 35.9078],
            '墨西哥': [-102.5528, 23.6345],
            'Mexico': [-102.5528, 23.6345],
            'MX': [-102.5528, 23.6345],
            '澳大利亚': [133.7751, -25.2744],
            'Australia': [133.7751, -25.2744],
            'AU': [133.7751, -25.2744],
        }
        return coordinates.get(country, [-95.7129, 37.0902])
    
    def get_industry_insights(self, watchlist_symbols: List[str]) -> List[Dict]:
        """获取盯盘股票的产业链洞察"""
        insights = []
        
        # 获取相关新闻
        all_news = []
        for symbol in watchlist_symbols[:5]:  # 限制5只股票避免过多API调用
            try:
                news = self.news_service.get_stock_news(symbol, limit=3)
                all_news.extend(news)
            except Exception as e:
                print(f"获取{symbol}新闻失败: {e}")
        
        # 如果没有新闻，返回默认洞见
        if not all_news:
            return [{
                'title': '等待新闻数据',
                'content': '暂时无法获取相关新闻数据，请稍后刷新或检查网络连接。',
                'related_stocks': watchlist_symbols,
                'sentiment': 'neutral'
            }]
        
        # 使用AI分析产业链动态
        system_prompt = """你是一个专业的产业链分析师。请基于提供的新闻，分析相关股票所在产业链的动态和形势。

请提供1-3个洞见判断，每个洞见应包含：
1. 细分市场动态分析
2. 产业链上下游影响
3. 国际/国内形势研判

请以JSON格式回复：
{
  "insights": [
    {
      "title": "洞见标题（不超过30字）",
      "content": "详细分析（100-200字）",
      "related_stocks": ["相关股票代码"],
      "sentiment": "positive/neutral/negative"
    }
  ]
}

今天是2026年3月10日。"""
        
        user_prompt = f"""请分析以下股票的产业链动态：

关注股票：{', '.join(watchlist_symbols)}

相关新闻：
"""
        for i, news in enumerate(all_news[:10], 1):
            user_prompt += f"\n{i}. {news.get('title', '')} ({news.get('source', '')})"
        
        user_prompt += "\n\n请提供1-3个产业链洞见判断。"
        
        try:
            response = self.ai_service._call_stepfun(system_prompt, user_prompt, max_tokens=800)
            
            # 解析AI响应
            import json
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                insights = result.get('insights', [])
                
            # 如果AI没有返回洞见，使用默认
            if not insights:
                insights = [{
                    'title': '产业链动态分析',
                    'content': f'基于{len(all_news)}条最新新闻，相关股票所在产业链整体保持稳定运行，建议持续关注市场动态和政策变化。',
                    'related_stocks': watchlist_symbols,
                    'sentiment': 'neutral'
                }]
        except Exception as e:
            print(f"产业链洞察分析失败: {e}")
            # 返回默认洞见
            insights = [{
                'title': '市场动态分析中',
                'content': '正在收集更多数据以提供深入的产业链洞察，请稍后刷新查看最新分析结果。',
                'related_stocks': watchlist_symbols,
                'sentiment': 'neutral'
            }]
        
        return insights
