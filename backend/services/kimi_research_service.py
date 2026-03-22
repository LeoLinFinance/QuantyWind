"""
Kimi Code 在线研究服务
使用Kimi-k2模型的web_search功能获取实时市场信息
"""
from openai import OpenAI
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KimiResearchService:
    """Kimi Code在线研究服务"""
    
    def __init__(self):
        import os
        # 使用OpenAI SDK连接Kimi API
        self.client = OpenAI(
            api_key=os.getenv('KIMI_API_KEY', ''),
            base_url="https://api.moonshot.cn/v1"
        )
        self.model = "kimi-k2-turbo-preview"
        
        # 声明使用内置的 web_search 工具
        self.tools = [{
            "type": "builtin_function",
            "function": {"name": "$web_search"}
        }]
        
        logger.info("✅ Kimi Research Service initialized with Kimi-k2")
    
    def research_stock(self, symbol: str, company_name: str = None) -> Dict:
        """
        研究股票的最新信息
        
        Args:
            symbol: 股票代码
            company_name: 公司名称（可选）
        
        Returns:
            研究结果字典
        """
        query = f"""请研究美股{symbol}公司的最新情况，提供以下信息：

1. 最近一个季度的财务表现（营收、利润、增长率）
2. 近期重大新闻和事件（最近1个月）
3. 分析师评级和目标价
4. 行业地位和竞争优势
5. 主要风险因素

请用简洁的语言总结，每个方面2-3句话即可。"""
        
        try:
            result = self._call_kimi_with_search(query)
            
            return {
                'symbol': symbol,
                'research_content': result,
                'timestamp': datetime.now().isoformat(),
                'source': 'kimi_k2_web_search'
            }
        except Exception as e:
            logger.error(f"Research failed for {symbol}: {e}")
            return {
                'symbol': symbol,
                'research_content': f"在线研究暂时不可用: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'source': 'error'
            }
    
    def research_industry(self, industry: str) -> Dict:
        """
        研究行业趋势
        
        Args:
            industry: 行业名称
        
        Returns:
            研究结果字典
        """
        query = f"""请分析{industry}行业的最新趋势：

1. 行业增长率和市场规模
2. 技术创新和变革
3. 政策法规影响
4. 主要参与者和竞争格局
5. 未来发展机会

请用简洁的语言总结，每个方面2-3句话即可。"""
        
        try:
            result = self._call_kimi_with_search(query)
            
            return {
                'industry': industry,
                'research_content': result,
                'timestamp': datetime.now().isoformat(),
                'source': 'kimi_k2_web_search'
            }
        except Exception as e:
            logger.error(f"Industry research failed for {industry}: {e}")
            return {
                'industry': industry,
                'research_content': f"行业研究暂时不可用: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'source': 'error'
            }
    
    def research_macro_environment(self) -> Dict:
        """
        研究宏观经济环境
        
        Returns:
            研究结果字典
        """
        query = """请分析当前美国宏观经济环境：

1. 最新经济指标（GDP、通胀、就业）
2. 美联储货币政策
3. 市场情绪和投资者信心
4. 主要风险因素
5. 对股市的影响

请用简洁的语言总结，每个方面2-3句话即可。"""
        
        try:
            result = self._call_kimi_with_search(query)
            
            return {
                'research_content': result,
                'timestamp': datetime.now().isoformat(),
                'source': 'kimi_k2_web_search'
            }
        except Exception as e:
            logger.error(f"Macro research failed: {e}")
            return {
                'research_content': f"宏观研究暂时不可用: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'source': 'error'
            }
    
    def _call_kimi_with_search(self, query: str, max_tokens: int = 2000) -> str:
        """
        调用Kimi-k2 API并启用web_search
        
        Args:
            query: 研究问题
            max_tokens: 最大token数（注意：k2模型会自动调整）
        
        Returns:
            研究结果文本
        """
        logger.info(f"🔍 调用Kimi-k2进行在线研究...")
        
        try:
            # 第一次请求
            messages = [{"role": "user", "content": query}]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                temperature=0.3
            )
            
            if not response.choices or len(response.choices) == 0:
                raise Exception("API返回空响应")
            
            message = response.choices[0].message
            
            # 检查是否需要处理tool_calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info("🔍 检测到web_search调用，获取最终结果...")
                
                # 将assistant的消息添加到对话历史
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                })
                
                # 添加tool响应
                for tool_call in message.tool_calls:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": ""
                    })
                
                # 第二次请求获取最终结果
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    temperature=0.3
                )
                
                if final_response.choices and len(final_response.choices) > 0:
                    content = final_response.choices[0].message.content
                    logger.info(f"✅ Kimi-k2研究成功: {len(content)} 字符, tokens: {final_response.usage.total_tokens if final_response.usage else 'N/A'}")
                    return content
                else:
                    raise Exception("第二次请求返回空响应")
            
            # 如果没有tool_calls，直接返回内容
            elif message.content:
                logger.info(f"✅ Kimi-k2研究成功: {len(message.content)} 字符")
                return message.content
            else:
                raise Exception("API返回空内容")
                
        except Exception as e:
            logger.error(f"❌ Kimi-k2 API调用异常: {type(e).__name__}: {e}")
            return f"在线研究失败: {str(e)}"
    
    def quick_research(self, symbol: str, aspect: str) -> str:
        """
        快速研究特定方面
        
        Args:
            symbol: 股票代码
            aspect: 研究方面（如：财务、新闻、评级等）
        
        Returns:
            研究结果文本
        """
        aspect_queries = {
            '财务': f'请简要总结{symbol}公司最近一个季度的财务表现',
            '新闻': f'请列出{symbol}公司最近1个月的重大新闻',
            '评级': f'请总结分析师对{symbol}的最新评级和目标价',
            '风险': f'请分析{symbol}公司当前面临的主要风险',
            '机会': f'请分析{symbol}公司的增长机会和投资亮点'
        }
        
        query = aspect_queries.get(aspect, f'请研究{symbol}的{aspect}')
        
        try:
            return self._call_kimi_with_search(query)
        except Exception as e:
            logger.error(f"Quick research failed: {e}")
            return f"快速研究失败: {str(e)}"
