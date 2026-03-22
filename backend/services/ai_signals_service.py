"""
AI智能交易信号分析服务
提供个股分析、交易信号、投资组合优化、市场趋势预测和风险监控功能
"""
import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

from .historical_data_service import HistoricalDataService
from .risk_service import RiskService
from .sentiment_service import SentimentService
from .ai_service import AIService
from .kimi_research_service import KimiResearchService

logger = logging.getLogger('ai_signals')
logger.setLevel(logging.INFO)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.cache_ttl = ttl  # 默认1小时
    
    def get_cache_key(self, operation: str, params: Dict) -> str:
        """生成缓存键"""
        params_str = json.dumps(params, sort_keys=True)
        return f"{operation}:{hash(params_str)}"
    
    def get(self, key: str) -> Optional[Dict]:
        """获取缓存"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"Cache hit: {key}")
                return data
            else:
                # 缓存过期，删除
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict):
        """设置缓存"""
        self.cache[key] = (data, time.time())
        logger.info(f"Cache set: {key}")
    
    def clear_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")


class AISignalsService:
    """AI信号服务"""
    
    def __init__(self):
        self.historical_service = HistoricalDataService()
        self.risk_service = RiskService()
        self.sentiment_service = SentimentService()
        self.ai_service = AIService()
        self.kimi_research = KimiResearchService()  # 新增Kimi研究服务
        self.cache_manager = CacheManager(ttl=3600)  # 1小时缓存
        
        # 从持久化存储加载自定义提示词
        from .persistence_service import PersistenceService
        self.persistence = PersistenceService()
        self.custom_prompts = self._load_custom_prompts()
        
        logger.info("AISignalsService initialized")
    
    def _load_custom_prompts(self) -> Dict:
        """加载自定义提示词"""
        settings = self.persistence.load_user_settings()
        return settings.get('ai_prompts', {})
    
    def _save_custom_prompts(self):
        """保存自定义提示词"""
        settings = self.persistence.load_user_settings()
        settings['ai_prompts'] = self.custom_prompts
        self.persistence.save_user_settings(settings)
    
    def get_custom_prompt(self, prompt_type: str) -> Optional[str]:
        """获取自定义提示词"""
        return self.custom_prompts.get(prompt_type)
    
    def set_custom_prompt(self, prompt_type: str, prompt: str):
        """设置自定义提示词"""
        self.custom_prompts[prompt_type] = prompt
        self._save_custom_prompts()
        logger.info(f"Custom prompt set for {prompt_type}")
    
    def analyze_stock(self, symbol: str) -> Dict:
        """
        个股智能分析
        
        Args:
            symbol: 股票代码
        
        Returns:
            分析结果字典
        """
        # 检查缓存
        cache_key = self.cache_manager.get_cache_key('analyze_stock', {'symbol': symbol})
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            cached_result['cached'] = True
            return cached_result
        
        logger.info(f"Analyzing stock: {symbol}")
        
        try:
            # 1. 收集历史数据
            historical_data = self.historical_service.get_symbol_data(symbol, is_index=False)
            if not historical_data or len(historical_data) < 20:
                raise InsufficientDataError(f"{symbol} 历史数据不足")
            
            # 2. 计算技术指标
            tech_indicators = calculate_technical_indicators(historical_data)
            
            # 3. 获取风险指标（使用单股组合）
            try:
                risk_metrics = self.risk_service.calculate_portfolio_risk([
                    {'symbol': symbol, 'weight': 1.0}
                ])
            except Exception as e:
                logger.warning(f"Failed to calculate risk metrics: {e}")
                risk_metrics = {}
            
            # 4. 获取舆情信息
            try:
                from .news_service import NewsService
                news_service = NewsService()
                news_list = news_service.get_stock_news(symbol, limit=3)
                sentiment = self.ai_service.analyze_sentiment(symbol, symbol)
            except Exception as e:
                logger.warning(f"Failed to get sentiment: {e}")
                news_list = []
                sentiment = "暂无舆情数据"
            
            # 4.5. 获取在线研究信息（使用Kimi Code）
            online_research = ""
            try:
                logger.info(f"🔍 使用Kimi Code研究 {symbol}...")
                research_result = self.kimi_research.research_stock(symbol)
                if research_result['source'] != 'error':
                    online_research = research_result['research_content']
                    logger.info(f"✅ 在线研究完成: {len(online_research)} 字符")
                else:
                    logger.warning(f"⚠️ 在线研究失败，使用基础分析")
            except Exception as e:
                logger.warning(f"Failed to get online research: {e}")
                online_research = ""
            
            # 5. 构建AI分析prompt
            current_price = historical_data[-1]['close']
            current_date = datetime.now().strftime('%Y年%m月%d日')
            
            # 使用自定义提示词（如果有）或默认提示词
            custom_prompt = self.get_custom_prompt('stock_analysis')
            if custom_prompt:
                system_prompt = custom_prompt.replace('{current_date}', current_date)
                logger.info("Using custom prompt for stock analysis")
            else:
                system_prompt = f"""你是一位资深的美股投资分析师，拥有20年的市场经验。
请基于提供的多维度数据，对指定股票进行全面分析和评分。

【评分标准】

1. 成长潜力（0-100分）
   - 90-100: 行业龙头，高速增长（年增长>30%），创新能力强，市场份额扩大
   - 70-89: 行业领先，稳定增长（年增长15-30%），有竞争优势
   - 50-69: 行业平均水平，增长一般（年增长5-15%）
   - 30-49: 增长放缓（年增长0-5%），面临挑战
   - 0-29: 增长停滞或负增长，市场份额萎缩

2. 风险等级（0-100分，分数越高风险越大）
   - 0-20: 极低风险（蓝筹股，波动率<15%，稳定盈利，现金流充足）
   - 21-40: 低风险（成熟企业，波动率15-25%，财务稳健）
   - 41-60: 中等风险（波动率25-35%，行业竞争激烈，盈利波动）
   - 61-80: 高风险（波动率35-50%，新兴行业，不确定性大）
   - 81-100: 极高风险（波动率>50%，亏损或生存危机，负面新闻多）

3. 估值水平（0-100分，分数越高越低估）
   - 90-100: 严重低估，P/E远低于行业平均30%以上，安全边际大
   - 70-89: 低估，P/E低于行业平均15-30%
   - 50-69: 合理估值，P/E接近行业平均（±15%）
   - 30-49: 高估，P/E高于行业平均15-30%
   - 0-29: 严重高估，P/E远高于行业平均30%以上，泡沫风险

【评分要求】
- 必须基于提供的实际数据（技术指标、风险指标、舆情、在线研究）进行评分
- 每个评分必须给出具体依据（30-50字）
- 评分要综合考虑技术面、基本面、舆情等多维度因素
- 评分要客观公正，不能过于乐观或悲观
- 如果数据不足，给出保守评分并说明原因

【分析框架】
1. 宏观环境分析：当前经济周期、利率环境、政策影响
2. 行业趋势：行业景气度、竞争格局、技术变革
3. 公司基本面：财务健康度、盈利能力、成长性
4. 技术面分析：价格趋势、支撑阻力、技术指标

今天是{current_date}。"""
            
            user_prompt = f"""请分析 {symbol} 的投资价值。

【历史价格数据】（最近{len(historical_data)}天，采样后展示最近20天）
{format_price_data(historical_data)}

【当前价格】${current_price:.2f}

【技术指标】
- MA5: ${tech_indicators['ma5']:.2f}, MA20: ${tech_indicators['ma20']:.2f}, MA60: ${tech_indicators['ma60']:.2f}
- MACD: {tech_indicators['macd']:.2f}
- RSI: {tech_indicators['rsi']:.1f}
- 布林带: 上轨${tech_indicators['bb_upper']:.2f}, 下轨${tech_indicators['bb_lower']:.2f}

【风险指标】
{format_risk_metrics(risk_metrics)}

【舆情信息】
{format_sentiment_data(sentiment, news_list)}

{f'''【在线研究信息】（来自Kimi Code实时搜索）
{online_research}
''' if online_research else ''}
请以JSON格式输出分析结果：
{{
    "macro_environment": "宏观环境分析（100-150字）",
    "industry_trend": "行业趋势分析（100-150字）",
    "fundamentals": "基本面分析（100-150字）",
    "technical_analysis": "技术面分析（100-150字）",
    "overall_score": 75.5,
    "key_metrics": {{
        "growth_potential": {{
            "score": 80,
            "reasoning": "评分依据（30-50字，必须基于实际数据）"
        }},
        "risk_level": {{
            "score": 45,
            "reasoning": "评分依据（30-50字，必须基于波动率、回撤等数据）"
        }},
        "valuation": {{
            "score": 70,
            "reasoning": "评分依据（30-50字，必须基于估值指标）"
        }}
    }},
    "summary": "一句话总结（20-30字）"
}}

注意：
1. 所有评分必须基于提供的实际数据
2. growth_potential要参考技术趋势、舆情、在线研究
3. risk_level要参考波动率、最大回撤、RSI等指标
4. valuation要参考当前价格、技术指标、行业对比
5. reasoning必须具体，不能泛泛而谈"""
            
            # 6. 调用AI服务（使用32k模型以支持更多上下文）
            ai_response = self.ai_service._call_stepfun(
                system_prompt, 
                user_prompt, 
                max_tokens=1000,
                model='step-1v-32k'  # AI智能分析使用32k模型
            )
            
            # 7. 解析AI响应
            analysis = self._parse_json_response(ai_response, {
                'macro_environment': '分析中...',
                'industry_trend': '分析中...',
                'fundamentals': '分析中...',
                'technical_analysis': '分析中...',
                'overall_score': 50.0,
                'key_metrics': {
                    'growth_potential': {'score': 50, 'reasoning': '数据不足'},
                    'risk_level': {'score': 50, 'reasoning': '数据不足'},
                    'valuation': {'score': 50, 'reasoning': '数据不足'}
                },
                'summary': '分析完成'
            })
            
            # 兼容旧格式：如果key_metrics是数字，转换为新格式
            if 'key_metrics' in analysis:
                metrics = analysis['key_metrics']
                if isinstance(metrics.get('growth_potential'), (int, float)):
                    analysis['key_metrics'] = {
                        'growth_potential': {
                            'score': metrics.get('growth_potential', 50),
                            'reasoning': '基于历史数据分析'
                        },
                        'risk_level': {
                            'score': metrics.get('risk_level', 50),
                            'reasoning': '基于波动率和回撤分析'
                        },
                        'valuation': {
                            'score': metrics.get('valuation', 50),
                            'reasoning': '基于技术指标分析'
                        }
                    }
            
            # 8. 构建结果
            result = {
                'symbol': symbol,
                'name': symbol,
                'current_price': current_price,
                'analysis': analysis,
                'data_sources': {
                    'historical_days': len(historical_data),
                    'news_count': len(news_list),
                    'risk_models_used': len(risk_metrics)
                },
                'timestamp': datetime.now().isoformat(),
                'cached': False
            }
            
            # 9. 缓存结果
            self.cache_manager.set(cache_key, result)
            
            return result
            
        except InsufficientDataError as e:
            logger.error(f"Insufficient data for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {e}")
            raise

    
    def generate_trading_signal(self, symbol: str) -> Dict:
        """
        生成交易信号
        
        Args:
            symbol: 股票代码
        
        Returns:
            交易信号字典
        """
        # 检查缓存
        cache_key = self.cache_manager.get_cache_key('trading_signal', {'symbol': symbol})
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            cached_result['cached'] = True
            return cached_result
        
        logger.info(f"Generating trading signal for: {symbol}")
        
        try:
            # 1. 获取历史数据
            historical_data = self.historical_service.get_symbol_data(symbol, is_index=False)
            if not historical_data or len(historical_data) < 20:
                raise InsufficientDataError(f"{symbol} 历史数据不足")
            
            # 2. 计算技术指标
            tech_indicators = calculate_technical_indicators(historical_data)
            current_price = historical_data[-1]['close']
            
            # 3. 获取风险指标
            try:
                risk_metrics = self.risk_service.calculate_portfolio_risk([
                    {'symbol': symbol, 'weight': 1.0}
                ])
            except Exception as e:
                logger.warning(f"Failed to calculate risk metrics: {e}")
                risk_metrics = {}
            
            # 4. 获取舆情
            try:
                from .news_service import NewsService
                news_service = NewsService()
                news_list = news_service.get_stock_news(symbol, limit=3)
                sentiment = self.ai_service.analyze_sentiment(symbol, symbol)
            except Exception as e:
                logger.warning(f"Failed to get sentiment: {e}")
                news_list = []
                sentiment = "暂无舆情数据"
            
            # 5. 判断趋势和位置
            trend = self._determine_trend(historical_data, tech_indicators)
            bb_position = self._determine_bb_position(current_price, tech_indicators)
            volume_trend = self._determine_volume_trend(historical_data)
            
            # 6. 构建交易信号prompt
            current_date = datetime.now().strftime('%Y年%m月%d日')
            
            # 使用自定义提示词（如果有）或默认提示词
            custom_prompt = self.get_custom_prompt('trading_signal')
            if custom_prompt:
                system_prompt = custom_prompt.replace('{current_date}', current_date)
                logger.info("Using custom prompt for trading signal")
            else:
                system_prompt = f"""你是一位专业的量化交易分析师。
请基于技术分析、基本面和舆情，给出明确的交易信号。

信号定义：
- strong_buy: 多个强烈买入信号，高置信度
- buy: 买入信号明确，中高置信度
- hold: 观望为主，信号不明确
- sell: 卖出信号明确，中高置信度
- strong_sell: 多个强烈卖出信号，高置信度

输出要求：
- 给出明确信号和置信度（0-100）
- 提供支撑位、阻力位、目标价、止损价
- 说明信号依据（技术、舆情、基本面）
- 使用JSON格式

今天是{current_date}。"""
            
            user_prompt = f"""请为 {symbol} 生成交易信号。

当前价格: ${current_price:.2f}

【技术指标】
- 价格趋势: {trend}
- RSI: {tech_indicators['rsi']:.1f} (超买>70, 超卖<30)
- MACD: {tech_indicators['macd']:.2f}
- 布林带位置: {bb_position}
- 成交量趋势: {volume_trend}
- MA5: ${tech_indicators['ma5']:.2f}, MA20: ${tech_indicators['ma20']:.2f}

【风险信号】
- 波动率: {risk_metrics.get('volatility', 0):.2%} (年化)
- 最大回撤: {risk_metrics.get('max_drawdown', 0):.2%}

【舆情】
{sentiment}

【新闻】
{format_sentiment_data('', news_list)}

请以JSON格式输出：
{{
    "signal": "buy",
    "confidence": 75,
    "support_level": 150.0,
    "resistance_level": 165.0,
    "target_price": 170.0,
    "stop_loss": 145.0,
    "reasoning": {{
        "technical": "技术面依据",
        "sentiment": "舆情依据",
        "fundamentals": "基本面依据"
    }}
}}"""
            
            # 7. 调用AI服务
            ai_response = self.ai_service._call_stepfun(system_prompt, user_prompt, max_tokens=800)
            
            # 8. 解析响应
            signal_data = self._parse_json_response(ai_response, {
                'signal': 'hold',
                'confidence': 50,
                'support_level': current_price * 0.95,
                'resistance_level': current_price * 1.05,
                'target_price': current_price * 1.10,
                'stop_loss': current_price * 0.90,
                'reasoning': {
                    'technical': '技术面分析中',
                    'sentiment': '舆情分析中',
                    'fundamentals': '基本面分析中'
                }
            })
            
            # 9. 验证信号有效性
            valid_signals = {'strong_buy', 'buy', 'hold', 'sell', 'strong_sell'}
            if signal_data['signal'] not in valid_signals:
                signal_data['signal'] = 'hold'
            
            # 10. 验证置信度范围
            signal_data['confidence'] = max(0, min(100, signal_data['confidence']))
            
            # 11. 构建结果
            result = {
                'symbol': symbol,
                'signal': signal_data['signal'],
                'confidence': float(signal_data.get('confidence', 50)),
                'current_price': current_price,
                'support_level': float(signal_data.get('support_level') or current_price * 0.95),
                'resistance_level': float(signal_data.get('resistance_level') or current_price * 1.05),
                'target_price': float(signal_data.get('target_price') or current_price * 1.10),
                'stop_loss': float(signal_data.get('stop_loss') or current_price * 0.90),
                'reasoning': signal_data.get('reasoning', {
                    'technical': '技术面分析中',
                    'sentiment': '舆情分析中',
                    'fundamentals': '基本面分析中'
                }),
                'timestamp': datetime.now().isoformat(),
                'cached': False
            }
            
            # 12. 缓存结果
            self.cache_manager.set(cache_key, result)
            
            return result
            
        except InsufficientDataError as e:
            logger.error(f"Insufficient data for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating trading signal for {symbol}: {e}")
            raise
    
    def optimize_portfolio(self, portfolio: List[Dict]) -> Dict:
        """
        投资组合优化
        
        Args:
            portfolio: 投资组合配置列表
        
        Returns:
            优化建议字典
        """
        logger.info(f"Optimizing portfolio with {len(portfolio)} positions")
        
        try:
            # TODO: 实现完整的组合优化逻辑
            result = {
                'current_analysis': {
                    'strengths': ['待实现'],
                    'weaknesses': ['待实现'],
                    'risk_metrics': {}
                },
                'recommendations': [],
                'projected_metrics': {
                    'expected_annual_return': 0.0,
                    'expected_volatility': 0.0,
                    'expected_sharpe': 0.0
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            raise

    
    def predict_market_trend(self, symbols: List[str], indices: List[str] = None) -> Dict:
        """
        市场趋势预测
        
        Args:
            symbols: 关注的股票列表
            indices: 关注的指数列表
        
        Returns:
            趋势预测字典
        """
        if indices is None:
            indices = ['^GSPC', '^IXIC', '^RUT']
        
        logger.info(f"Predicting market trend for {len(symbols)} stocks and {len(indices)} indices")
        
        try:
            # TODO: 实现完整的趋势预测逻辑
            result = {
                'predictions': {
                    'short_term': {
                        'period': '1_week',
                        'direction': 'sideways',
                        'magnitude': 0.0,
                        'probability': 0.5
                    },
                    'medium_term': {
                        'period': '1_month',
                        'direction': 'sideways',
                        'magnitude': 0.0,
                        'probability': 0.5
                    },
                    'long_term': {
                        'period': '3_months',
                        'direction': 'sideways',
                        'magnitude': 0.0,
                        'probability': 0.5
                    }
                },
                'influencing_factors': [],
                'scenarios': [],
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting market trend: {e}")
            raise
    
    def monitor_risks(self, portfolio: List[Dict], thresholds: Dict = None) -> Dict:
        """
        风险监控
        
        Args:
            portfolio: 投资组合列表
            thresholds: 风险阈值配置
        
        Returns:
            风险预警字典
        """
        if thresholds is None:
            thresholds = {
                'volatility': 0.25,
                'drawdown': 0.15,
                'sentiment': -0.3
            }
        
        logger.info(f"Monitoring risks for {len(portfolio)} positions")
        
        try:
            # TODO: 实现完整的风险监控逻辑
            result = {
                'alerts': [],
                'portfolio_risk_score': 50.0,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error monitoring risks: {e}")
            raise


    def _parse_json_response(self, response: str, default: Dict) -> Dict:
        """
        解析AI的JSON响应

        Args:
            response: AI响应文本
            default: 默认值

        Returns:
            解析后的字典
        """
        try:
            # 尝试提取JSON
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in AI response")
                return default
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return default

    def _determine_trend(self, data: List[Dict], indicators: Dict) -> str:
        """判断价格趋势"""
        current_price = data[-1]['close']
        ma20 = indicators['ma20']
        ma60 = indicators['ma60']

        if current_price > ma20 > ma60:
            return "上升趋势"
        elif current_price < ma20 < ma60:
            return "下降趋势"
        else:
            return "震荡趋势"

    def _determine_bb_position(self, price: float, indicators: Dict) -> str:
        """判断布林带位置"""
        bb_upper = indicators['bb_upper']
        bb_lower = indicators['bb_lower']
        bb_mid = (bb_upper + bb_lower) / 2

        if price > bb_upper:
            return "超买区域（布林带上轨之上）"
        elif price < bb_lower:
            return "超卖区域（布林带下轨之下）"
        elif price > bb_mid:
            return "中性偏强（布林带中轨之上）"
        else:
            return "中性偏弱（布林带中轨之下）"

    def _determine_volume_trend(self, data: List[Dict]) -> str:
        """判断成交量趋势"""
        if len(data) < 10:
            return "数据不足"

        recent_volume = np.mean([d['volume'] for d in data[-5:]])
        avg_volume = np.mean([d['volume'] for d in data[-20:]])

        if recent_volume > avg_volume * 1.5:
            return "放量"
        elif recent_volume < avg_volume * 0.7:
            return "缩量"
        else:
            return "正常"




# ============================================================================
# 数据处理工具函数
# ============================================================================

def smart_sample(data: List[Dict], target_points: int = 100) -> List[Dict]:
    """
    智能采样历史数据
    
    采样策略：
    - 最近3个月：每日数据（约63个点）
    - 3-12个月：每周数据（约36个点）
    - 1-5年：每月数据（约48个点）
    
    Args:
        data: 历史数据列表
        target_points: 目标数据点数
    
    Returns:
        采样后的数据列表
    """
    if len(data) <= target_points:
        return data
    
    # 分段采样
    recent_3m = data[-63:] if len(data) >= 63 else data  # 最近3个月，每日
    recent_9m = data[-252:-63:7] if len(data) >= 252 else []  # 3-12个月，每周
    older = data[:-252:30] if len(data) > 252 else []  # 1-5年，每月
    
    sampled = older + recent_9m + recent_3m
    
    # 如果还是太多，进一步采样
    if len(sampled) > target_points:
        step = len(sampled) // target_points
        sampled = sampled[::step]
    
    return sampled


def calculate_technical_indicators(data: List[Dict]) -> Dict:
    """
    计算技术指标
    
    Args:
        data: 历史价格数据
    
    Returns:
        技术指标字典
    """
    if not data or len(data) < 20:
        return {
            'ma5': 0, 'ma10': 0, 'ma20': 0, 'ma60': 0,
            'macd': 0, 'rsi': 50, 'bb_upper': 0, 'bb_lower': 0
        }
    
    closes = np.array([d['close'] for d in data])
    
    # 移动平均线
    ma5 = float(np.mean(closes[-5:])) if len(closes) >= 5 else float(closes[-1])
    ma10 = float(np.mean(closes[-10:])) if len(closes) >= 10 else float(closes[-1])
    ma20 = float(np.mean(closes[-20:])) if len(closes) >= 20 else float(closes[-1])
    ma60 = float(np.mean(closes[-60:])) if len(closes) >= 60 else float(closes[-1])
    
    # RSI
    rsi = calculate_rsi(closes)
    
    # MACD
    macd = calculate_macd(closes)
    
    # 布林带
    bb_upper, bb_lower = calculate_bollinger_bands(closes)
    
    return {
        'ma5': ma5,
        'ma10': ma10,
        'ma20': ma20,
        'ma60': ma60,
        'macd': macd,
        'rsi': rsi,
        'bb_upper': bb_upper,
        'bb_lower': bb_lower
    }



def calculate_rsi(closes: np.ndarray, period: int = 14) -> float:
    """计算RSI指标"""
    if len(closes) < period + 1:
        return 50.0
    
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)


def calculate_macd(closes: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> float:
    """计算MACD指标"""
    if len(closes) < slow:
        return 0.0
    
    # 计算EMA
    ema_fast = calculate_ema(closes, fast)
    ema_slow = calculate_ema(closes, slow)
    
    macd_line = ema_fast - ema_slow
    
    return float(macd_line)


def calculate_ema(data: np.ndarray, period: int) -> float:
    """计算指数移动平均"""
    if len(data) < period:
        return float(np.mean(data))
    
    multiplier = 2 / (period + 1)
    ema = np.mean(data[:period])
    
    for price in data[period:]:
        ema = (price - ema) * multiplier + ema
    
    return float(ema)


def calculate_bollinger_bands(closes: np.ndarray, period: int = 20, std_dev: int = 2) -> tuple:
    """计算布林带"""
    if len(closes) < period:
        current_price = float(closes[-1])
        return current_price, current_price
    
    sma = np.mean(closes[-period:])
    std = np.std(closes[-period:])
    
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    
    return float(upper_band), float(lower_band)


def format_price_data(data: List[Dict], max_points: int = 100) -> str:
    """格式化价格数据为AI可读格式"""
    sampled = smart_sample(data, max_points)
    
    formatted = []
    for item in sampled[-20:]:  # 只显示最近20个点
        formatted.append(
            f"{item['date']}: 开${item['open']:.2f} 高${item['high']:.2f} "
            f"低${item['low']:.2f} 收${item['close']:.2f} 量{item['volume']:,}"
        )
    
    return '\n'.join(formatted)


def format_risk_metrics(metrics: Dict) -> str:
    """格式化风险指标"""
    return f"""
- 年化波动率: {metrics.get('volatility', 0):.2%}
- 夏普比率: {metrics.get('sharpe_ratio', 0):.2f}
- Sortino比率: {metrics.get('sortino_ratio', 0):.2f}
- 最大回撤: {metrics.get('max_drawdown', 0):.2%}
- Beta系数: {metrics.get('beta', 1.0):.2f}
- VaR(95%): {metrics.get('var_95', 0):.2%}
- CVaR(95%): {metrics.get('cvar_95', 0):.2%}
    """.strip()


def format_sentiment_data(sentiment: str, news_list: List[Dict]) -> str:
    """格式化舆情数据"""
    news_summary = []
    for i, news in enumerate(news_list[:3], 1):
        news_summary.append(f"{i}. {news.get('title', '')} ({news.get('source', '')})")
    
    return f"""
舆情分析: {sentiment}

最新新闻:
{chr(10).join(news_summary) if news_summary else '暂无新闻'}
    """.strip()

    
    def _parse_json_response(self, response: str, default: Dict) -> Dict:
        """
        解析AI的JSON响应
        
        Args:
            response: AI响应文本
            default: 默认值
        
        Returns:
            解析后的字典
        """
        try:
            # 尝试提取JSON
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in AI response")
                return default
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return default


# ============================================================================
# 自定义异常
# ============================================================================

class AIAPIError(Exception):
    """AI API调用失败"""
    pass


class AIResponseParseError(Exception):
    """AI响应解析失败"""
    pass


class InsufficientDataError(Exception):
    """数据不足，无法进行分析"""
    pass
