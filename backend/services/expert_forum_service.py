"""
智者论坛服务
整合新闻总结和专家agent分析
"""
import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from services.news_summary_service import NewsSummaryService
from services.kimi_research_service import KimiResearchService
from services.portfolio_service import PortfolioService
from services.expert_forum_chat_service import ExpertForumChatService
from openai import OpenAI

logger = logging.getLogger(__name__)

class ExpertForumService:
    """智者论坛服务"""
    
    def __init__(self):
        self.news_summary_service = NewsSummaryService()
        self.kimi_service = KimiResearchService()
        self.portfolio_service = PortfolioService()
        self.config_file = Path("data/expert_configs.json")
        self.summary_prompt_file = Path("data/summary_prompt.txt")
        self.config_file.parent.mkdir(exist_ok=True)
        
        # 初始化聊天服务
        self.chat_service = ExpertForumChatService()
        
        # 为每个专家分配独立的StepFun API Key（从环境变量读取，如果未配置则使用默认）
        # 用户可以在设置页面配置自己的 API Key
        default_key = os.getenv('STEPFUN_API_KEY', '')
        self.expert_api_keys = {
            'stock_analyst': os.getenv('STEPFUN_API_KEY_STOCK_ANALYST', default_key),
            'industry_analyst': os.getenv('STEPFUN_API_KEY_INDUSTRY_ANALYST', default_key),
            'market_analyst': os.getenv('STEPFUN_API_KEY_MARKET_ANALYST', default_key),
            'value_investor': os.getenv('STEPFUN_API_KEY_VALUE_INVESTOR', default_key),
            'chief_economist': os.getenv('STEPFUN_API_KEY_CHIEF_ECONOMIST', default_key)
        }
        
        self.stepfun_base_url = "https://api.stepfun.com/v1"
        self.stepfun_model = "step-1-256k"  # 使用256k上下文窗口的模型，支持超长对话
        
        # 确保配置文件存在
        if not self.config_file.exists():
            self.config_file.write_text("[]")
        
        # 确保总结提示词文件存在
        if not self.summary_prompt_file.exists():
            default_prompt = self.news_summary_service.get_default_prompt()
            self.summary_prompt_file.write_text(default_prompt, encoding='utf-8')
        
        logger.info("✅ Expert Forum Service initialized with dedicated API keys for each expert")
    
    async def fetch_news_summary(self, last_time: Optional[str] = None) -> Dict:
        """
        获取新闻资讯总结（使用StepFun API）
        
        Args:
            last_time: 上次获取资讯的时间
        
        Returns:
            新闻总结内容
        """
        try:
            # 读取自定义总结提示词
            custom_prompt = None
            if self.summary_prompt_file.exists():
                custom_prompt = self.summary_prompt_file.read_text(encoding='utf-8')
            
            # 使用新闻总结服务
            result = self.news_summary_service.summarize_news(
                custom_prompt=custom_prompt,
                last_time=last_time
            )
            
            # 将新闻总结添加到聊天历史
            await self.chat_service.add_news_summary(
                summary_content=result['summary'],
                stock_symbols=result['portfolio_symbols']
            )
            
            return {
                'content': result['summary'],
                'timestamp': result['timestamp'],
                'stock_symbols': result['portfolio_symbols'],
                'news_count': result['news_count']
            }
            
        except Exception as e:
            logger.error(f"获取新闻总结失败: {e}")
            raise
    
    async def stop_news_feed(self):
        """
        通知KimiClaw停止推送
        """
        logger.info("📴 KimiClaw资讯推送已停止")
        # 这里可以添加额外的清理逻辑
        return {"status": "stopped"}
    
    async def get_expert_analysis(
        self,
        expert_id: str,
        expert_name: str,
        expert_prompt: str,
        context: str,
        model: str = None  # 添加模型参数
    ) -> Dict:
        """
        获取专家分析
        
        Args:
            expert_id: 专家ID
            expert_name: 专家名称
            expert_prompt: 专家提示词
            context: 上下文信息（包含最后一次资讯总结）
        
        Returns:
            专家分析结果
        """
        try:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            # 获取当前股票价格和持仓信息
            portfolio = self.portfolio_service.get_portfolio()
            holdings = portfolio.get('holdings', [])
            
            # 获取股票实时价格（并行）
            from services.yahoo_finance_api import YahooFinanceAPI
            yahoo_api = YahooFinanceAPI()
            
            holdings_with_price = []
            
            if holdings:
                # 并行获取所有股票价格
                with ThreadPoolExecutor(max_workers=5) as executor:
                    loop = asyncio.get_event_loop()
                    tasks = [
                        loop.run_in_executor(executor, yahoo_api.get_stock_quote, holding['symbol'])
                        for holding in holdings
                    ]
                    quotes = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                for holding, quote in zip(holdings, quotes):
                    symbol = holding['symbol']
                    if isinstance(quote, Exception) or not quote:
                        logger.warning(f"获取{symbol}价格失败，使用成本价")
                        holdings_with_price.append({
                            'symbol': symbol,
                            'name': symbol,
                            'shares': holding['shares'],
                            'cost_basis': holding['cost_basis'],
                            'current_price': holding['cost_basis'],
                            'change': 0,
                            'change_percent': 0,
                            'market_value': holding['shares'] * holding['cost_basis'],
                            'profit_loss': 0,
                            'profit_loss_percent': 0
                        })
                    else:
                        holdings_with_price.append({
                            'symbol': symbol,
                            'name': quote.get('name', symbol),
                            'shares': holding['shares'],
                            'cost_basis': holding['cost_basis'],
                            'current_price': quote.get('price', 0),
                            'change': quote.get('change', 0),
                            'change_percent': quote.get('changePercent', 0),
                            'market_value': holding['shares'] * quote.get('price', 0),
                            'profit_loss': holding['shares'] * (quote.get('price', 0) - holding['cost_basis']),
                            'profit_loss_percent': ((quote.get('price', 0) - holding['cost_basis']) / holding['cost_basis'] * 100) if holding['cost_basis'] > 0 else 0
                        })
            
            # 从聊天服务获取上下文（包含总结和历史消息）
            chat_context = await self.chat_service.get_context_for_expert()
            
            # 构建用户查询（不包含expert_prompt，它会作为system消息）
            full_query = f"""【对话历史】
{chat_context if chat_context else '暂无对话历史'}

【当前持仓详情】
"""
            
            total_market_value = 0
            total_cost = 0
            
            for holding in holdings_with_price:
                full_query += f"\n{holding['symbol']} - {holding['name']}"
                full_query += f"\n  持仓: {holding['shares']}股"
                full_query += f"\n  成本价: ${holding['cost_basis']:.2f}"
                full_query += f"\n  当前价: ${holding['current_price']:.2f} ({holding['change_percent']:+.2f}%)"
                full_query += f"\n  市值: ${holding['market_value']:,.2f}"
                full_query += f"\n  盈亏: ${holding['profit_loss']:+,.2f} ({holding['profit_loss_percent']:+.2f}%)"
                full_query += f"\n"
                
                total_market_value += holding['market_value']
                total_cost += holding['shares'] * holding['cost_basis']
            
            total_profit_loss = total_market_value - total_cost
            total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
            
            full_query += f"\n【投资组合总览】"
            full_query += f"\n  总市值: ${total_market_value:,.2f}"
            full_query += f"\n  总成本: ${total_cost:,.2f}"
            full_query += f"\n  总盈亏: ${total_profit_loss:+,.2f} ({total_profit_loss_percent:+.2f}%)"
            full_query += f"\n  现金余额: ${portfolio.get('cash', 0):,.2f}"
            
            full_query += "\n\n请根据以上对话历史、最新资讯和持仓情况，提供你的专业分析和建议。"
            
            # 调用StepFun进行分析（添加超时控制）
            logger.info(f"开始调用{expert_name}进行分析（使用专属API Key）...")
            with ThreadPoolExecutor() as executor:
                loop = asyncio.get_event_loop()
                try:
                    analysis = await asyncio.wait_for(
                        loop.run_in_executor(
                            executor,
                            self._call_stepfun_for_analysis,
                            expert_id,  # 传入expert_id以选择对应的API Key
                            expert_prompt,
                            full_query,
                            model  # 传入模型参数
                        ),
                        timeout=70.0  # 70秒超时（给HTTP 60秒超时留出余地）
                    )
                    logger.info(f"{expert_name}分析完成，长度: {len(analysis)}")
                except asyncio.TimeoutError:
                    logger.error(f"{expert_name}分析超时（70秒）")
                    analysis = f"抱歉，{expert_name}分析超时。这可能是由于网络问题或查询过于复杂。请稍后重试。"
                except Exception as e:
                    logger.error(f"{expert_name}分析失败: {e}")
                    raise
            
            # 检查专家是否选择不回复
            should_skip = "无需回复" in analysis
            
            # 只有当专家选择回复时，才添加到聊天历史和返回结果
            if not should_skip:
                # 将专家回复添加到聊天历史
                await self.chat_service.add_expert_response(
                    expert_type=expert_name,
                    content=analysis
                )
                
                return {
                    'expert_id': expert_id,
                    'expert_name': expert_name,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat(),
                    'holdings_analyzed': len(holdings_with_price)
                }
            else:
                # 专家选择不回复，返回None表示跳过
                logger.info(f"{expert_name}选择不回复此次讨论")
                return None
            
        except Exception as e:
            logger.error(f"{expert_name}分析失败: {e}")
            raise
    
    async def get_expert_configs(self) -> List[Dict]:
        """
        获取专家配置
        """
        try:
            if self.config_file.exists():
                content = self.config_file.read_text()
                return json.loads(content) if content.strip() else []
            return []
        except Exception as e:
            logger.error(f"读取专家配置失败: {e}")
            return []
    
    async def save_expert_config(self, config: Dict):
        """
        保存专家配置
        
        Args:
            config: 专家配置字典
        """
        try:
            configs = await self.get_expert_configs()
            
            # 更新或添加配置
            found = False
            for i, c in enumerate(configs):
                if c['id'] == config['id']:
                    configs[i] = config
                    found = True
                    break
            
            if not found:
                configs.append(config)
            
            # 保存到文件
            self.config_file.write_text(json.dumps(configs, ensure_ascii=False, indent=2))
            logger.info(f"✅ 专家配置已保存: {config['name']}")
            
        except Exception as e:
            logger.error(f"保存专家配置失败: {e}")
            raise
    
    async def get_summary_prompt(self) -> str:
        """
        获取资讯总结提示词
        """
        try:
            if self.summary_prompt_file.exists():
                return self.summary_prompt_file.read_text(encoding='utf-8')
            return self.news_summary_service.get_default_prompt()
        except Exception as e:
            logger.error(f"读取总结提示词失败: {e}")
            return self.news_summary_service.get_default_prompt()
    
    async def save_summary_prompt(self, prompt: str):
        """
        保存资讯总结提示词
        
        Args:
            prompt: 新的提示词
        """
        try:
            self.summary_prompt_file.write_text(prompt, encoding='utf-8')
            logger.info("✅ 资讯总结提示词已保存")
        except Exception as e:
            logger.error(f"保存总结提示词失败: {e}")
            raise


    async def add_user_message(self, content: str) -> Dict:
        """
        添加用户消息到对话
        
        Args:
            content: 用户消息内容
        
        Returns:
            消息信息
        """
        try:
            message = await self.chat_service.add_user_message(content)
            return {
                'id': message.id,
                'role': message.role.value,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'intent': message.intent.value if message.intent else None
            }
        except Exception as e:
            logger.error(f"添加用户消息失败: {e}")
            raise
    
    async def get_conversation_history(self) -> List[Dict]:
        """
        获取对话历史
        
        Returns:
            对话消息列表
        """
        try:
            messages = await self.chat_service.get_conversation_history()
            return [
                {
                    'id': msg.id,
                    'role': msg.role.value,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'expert_type': msg.expert_type,
                    'intent': msg.intent.value if msg.intent else None
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    async def reset_conversation(self):
        """
        重置对话
        """
        try:
            await self.chat_service.reset_conversation()
            logger.info("✅ 对话已重置")
        except Exception as e:
            logger.error(f"重置对话失败: {e}")
            raise
    
    def get_chat_stats(self) -> Dict:
        """
        获取聊天统计信息
        
        Returns:
            统计信息
        """
        return {
            'message_count': self.chat_service.get_message_count(),
            'has_summary': self.chat_service.has_active_summary()
        }
    
    def _call_stepfun_for_analysis(self, expert_id: str, system_prompt: str, user_query: str, model: str = None) -> str:
        """
        调用StepFun API进行专家分析（使用专家专属API Key）
        
        Args:
            expert_id: 专家ID，用于选择对应的API Key
            system_prompt: 专家的系统提示词
            user_query: 用户查询（包含持仓和上下文）
            model: 使用的模型名称，如果为None则使用默认模型
        
        Returns:
            分析结果
        """
        try:
            # 根据expert_id获取对应的API Key
            api_key = self.expert_api_keys.get(expert_id)
            if not api_key:
                logger.warning(f"未找到专家 {expert_id} 的专属API Key，使用默认Key")
                api_key = self.expert_api_keys.get('stock_analyst')  # 使用默认Key
            
            # 确定使用的模型
            selected_model = model if model else self.stepfun_model
            
            # 为每个专家创建独立的客户端，设置HTTP超时
            client = OpenAI(
                api_key=api_key,
                base_url=self.stepfun_base_url,
                timeout=60.0  # 设置60秒HTTP超时
            )
            
            logger.info(f"使用专家 {expert_id} 的专属API Key: {api_key[:20]}...")
            logger.info(f"模型: {selected_model}, 系统提示词长度: {len(system_prompt)}, 用户查询长度: {len(user_query)}")
            
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                max_tokens=2000  # 增加到2000以支持更长的回复
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                tokens = response.usage.total_tokens if response.usage else 'N/A'
                logger.info(f"✅ StepFun分析成功 ({expert_id}): {len(content)} 字符, tokens: {tokens}")
                return content
            else:
                raise Exception("API返回空响应")
                
        except Exception as e:
            logger.error(f"❌ StepFun API调用失败 ({expert_id}): {type(e).__name__}: {e}")
            # 记录更详细的错误信息
            if hasattr(e, 'response'):
                logger.error(f"响应状态码: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
                logger.error(f"响应内容: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
            raise

