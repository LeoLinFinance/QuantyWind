"""
阶跃星辰 AI 服务
用于投资组合风险解读
"""
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class StepFunService:
    """阶跃星辰 AI 服务"""
    
    def __init__(self):
        self.api_key = os.getenv('STEPFUN_API_KEY', '')
        self.base_url = "https://api.stepfun.com/v1/chat/completions"
        self.model = "step-1-8k"
    
    def interpret_portfolio_risk(
        self,
        portfolio: List[Dict],
        risk_metrics: Dict
    ) -> str:
        """
        解读投资组合风险指标
        
        Args:
            portfolio: 投资组合配置 [{'symbol': 'AAPL', 'weight': 0.3, 'name': 'Apple Inc.'}, ...]
            risk_metrics: 风险指标字典
        
        Returns:
            风险解读文本
        """
        # 构建提示词
        prompt = self._build_risk_interpretation_prompt(portfolio, risk_metrics)
        
        # 调用API
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位专业的投资顾问，擅长用通俗易懂的语言向投资小白解释复杂的金融风险指标。你的目标是帮助用户理解他们的投资组合风险，并给出实用的建议。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"❌ 阶跃星辰API调用失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return self._get_fallback_interpretation(portfolio, risk_metrics)
                
        except Exception as e:
            print(f"❌ 调用阶跃星辰API时出错: {str(e)}")
            return self._get_fallback_interpretation(portfolio, risk_metrics)
    
    def _build_risk_interpretation_prompt(
        self,
        portfolio: List[Dict],
        risk_metrics: Dict
    ) -> str:
        """构建风险解读提示词"""
        
        # 格式化投资组合信息
        portfolio_info = "\n".join([
            f"- {item['symbol']} ({item.get('name', item['symbol'])}): {item['weight']*100:.1f}%"
            for item in portfolio
        ])
        
        # 格式化风险指标
        metrics_info = f"""
VaR (95%置信度): {risk_metrics['var_95']*100:.2f}%
CVaR (95%置信度): {risk_metrics['cvar_95']*100:.2f}%
年化波动率: {risk_metrics['volatility']*100:.2f}%
年化收益率: {risk_metrics['annual_return']*100:.2f}%
夏普比率: {risk_metrics['sharpe_ratio']:.2f}
Sortino比率: {risk_metrics['sortino_ratio']:.2f}
最大回撤: {risk_metrics['max_drawdown']*100:.2f}%
Beta系数: {risk_metrics['beta']:.2f}
偏度: {risk_metrics['skewness']:.2f}
峰度: {risk_metrics['kurtosis']:.2f}
"""
        
        prompt = f"""我是一个投资小白，刚刚配置了一个投资组合，想了解这个组合的风险情况。请用通俗易懂的语言帮我解读这些风险指标。

【我的投资组合】
{portfolio_info}

【计算出的风险指标】
{metrics_info}

请帮我解答以下问题：

1. **整体风险评估**：这个投资组合的风险水平如何？是高风险、中风险还是低风险？

2. **关键指标解读**：
   - VaR和CVaR这两个数字代表什么意思？对我来说意味着什么？
   - 年化波动率{risk_metrics['volatility']*100:.2f}%是高还是低？
   - 夏普比率{risk_metrics['sharpe_ratio']:.2f}说明了什么？
   - 最大回撤{risk_metrics['max_drawdown']*100:.2f}%意味着什么？
   - Beta系数{risk_metrics['beta']:.2f}告诉我什么信息？

3. **股票风险贡献**：
   - 哪些股票对整体风险的影响更大？为什么？
   - 这些股票之间的相关性如何？

4. **实用建议**：
   - 基于这些风险指标，我应该注意什么？
   - 如果我想降低风险，可以怎么调整？
   - 这个组合适合什么样的投资者？

请用简单的语言，就像和朋友聊天一样，帮我理解这些数字背后的含义。避免使用过多专业术语，如果必须使用，请解释清楚。
"""
        
        return prompt
    
    def _get_fallback_interpretation(
        self,
        portfolio: List[Dict],
        risk_metrics: Dict
    ) -> str:
        """当API调用失败时的备用解读"""
        
        var_95 = risk_metrics['var_95'] * 100
        volatility = risk_metrics['volatility'] * 100
        sharpe = risk_metrics['sharpe_ratio']
        max_dd = risk_metrics['max_drawdown'] * 100
        beta = risk_metrics['beta']
        
        # 风险等级判断
        if volatility < 15:
            risk_level = "低风险"
        elif volatility < 25:
            risk_level = "中等风险"
        else:
            risk_level = "高风险"
        
        interpretation = f"""
## 投资组合风险解读

### 整体风险评估
您的投资组合属于**{risk_level}**水平（年化波动率{volatility:.2f}%）。

### 关键指标说明

**VaR (95%)：{var_95:.2f}%**
这个数字的意思是：在正常市场情况下，您的投资组合单日损失超过{var_95:.2f}%的概率只有5%。换句话说，95%的情况下，您的单日损失不会超过这个数字。

**年化波动率：{volatility:.2f}%**
这是衡量投资组合价格波动程度的指标。数值越大，价格波动越剧烈，风险越高。

**夏普比率：{sharpe:.2f}**
这个比率衡量的是"每承担一单位风险，能获得多少超额收益"。一般来说：
- 大于1：表现不错
- 大于2：表现优秀
- 小于1：可能需要优化

**最大回撤：{max_dd:.2f}%**
这是历史上从最高点到最低点的最大跌幅。意味着在过去的数据中，您的投资组合最多曾经跌过{max_dd:.2f}%。

**Beta系数：{beta:.2f}**
- Beta < 1：您的组合波动小于市场整体
- Beta = 1：与市场同步波动
- Beta > 1：波动大于市场，风险和收益都可能更高

### 投资建议

1. **风险承受能力**：这个组合适合能够承受{risk_level}的投资者
2. **持有期限**：建议至少持有6-12个月，以平滑短期波动
3. **定期检查**：建议每月检查一次组合表现，必要时进行调整

### 注意事项
- 历史数据不代表未来表现
- 市场环境变化可能导致风险指标变化
- 建议根据个人风险承受能力调整投资组合

---
*本解读基于历史数据计算，仅供参考，不构成投资建议。*
"""
        
        return interpretation
