# AI智能交易信号分析 - 设计文档

## 概述

本设计文档描述了AI智能交易信号分析功能的技术实现方案。该功能利用阶跃星辰Step 3.5 Flash 32k大模型，结合5年历史价格数据、风险指标和实时舆情分析，为用户提供智能的个股分析、交易信号预测、投资组合优化建议、市场趋势预测和风险预警。

### 核心目标

1. 为个股提供多维度AI分析（宏观、行业、基本面、技术面）
2. 生成可操作的买入/卖出交易信号
3. 提供投资组合优化建议
4. 预测市场趋势（短期、中期、长期）
5. 实时监控并预警投资风险

### 技术栈

- AI模型：阶跃星辰 Step 3.5 Flash 32k
- 后端：Python FastAPI
- 前端：React + TypeScript
- 数据源：历史数据服务、风险服务、舆情服务、新闻服务

## 架构设计

### 系统架构

```
┌─────────────────┐
│   前端UI层      │
│  (React/TS)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API路由层     │
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI信号服务层   │
│ (ai_signals.py) │
└────────┬────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 历史数据服务 │  │  风险服务    │  │  舆情服务    │  │  AI服务      │
│ (5年数据)    │  │ (20+模型)    │  │ (新闻+情绪)  │  │ (Step 3.5)   │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### 数据流

1. **用户请求** → API路由层
2. **数据收集** → 从各服务获取历史数据、风险指标、舆情信息
3. **数据处理** → 格式化、采样、计算技术指标
4. **AI分析** → 构建Prompt，调用AI模型
5. **结果解析** → 解析AI响应，提取结构化数据
6. **缓存管理** → 缓存结果（1小时有效期）
7. **返回响应** → 返回给前端展示

## 组件和接口

### 1. AI信号服务 (AISignalsService)

核心服务类，负责协调各个数据源并调用AI模型。

#### 主要方法

```python
class AISignalsService:
    def __init__(self):
        self.historical_service = HistoricalDataService()
        self.risk_service = RiskService()
        self.sentiment_service = SentimentService()
        self.ai_service = AIService()
        self.cache = {}  # 缓存AI分析结果
    
    def analyze_stock(self, symbol: str) -> Dict
    def generate_trading_signal(self, symbol: str) -> Dict
    def optimize_portfolio(self, portfolio: List[Dict]) -> Dict
    def predict_market_trend(self, symbols: List[str]) -> Dict
    def monitor_risks(self, portfolio: List[Dict]) -> List[Dict]
```

### 2. API路由 (router)

提供RESTful API端点。

```python
# GET /api/ai-signals/analyze/{symbol}
# 个股智能分析
Response: {
    "symbol": str,
    "analysis": {
        "macro_environment": str,
        "industry_trend": str,
        "fundamentals": str,
        "technical_analysis": str,
        "overall_score": float,  # 0-100
        "key_metrics": Dict
    },
    "timestamp": str,
    "cached": bool
}

# GET /api/ai-signals/trading-signal/{symbol}
# 买入/卖出信号
Response: {
    "symbol": str,
    "signal": str,  # "strong_buy" | "buy" | "hold" | "sell" | "strong_sell"
    "confidence": float,  # 0-100
    "support_level": float,
    "resistance_level": float,
    "target_price": float,
    "stop_loss": float,
    "reasoning": {
        "technical": str,
        "sentiment": str,
        "fundamentals": str
    },
    "timestamp": str
}

# POST /api/ai-signals/optimize-portfolio
# 投资组合优化
Request: {
    "portfolio": [
        {"symbol": str, "weight": float, "shares": int, "cost_basis": float}
    ]
}
Response: {
    "current_analysis": {
        "strengths": List[str],
        "weaknesses": List[str],
        "risk_metrics": Dict
    },
    "recommendations": [
        {"action": str, "symbol": str, "percentage": float, "reasoning": str}
    ],
    "projected_metrics": {
        "expected_return": float,
        "expected_risk": float,
        "sharpe_ratio": float
    }
}

# POST /api/ai-signals/market-trend
# 市场趋势预测
Request: {
    "symbols": List[str],  # 关注的股票列表
    "indices": List[str]   # 关注的指数列表
}
Response: {
    "predictions": {
        "short_term": {  # 1周
            "direction": str,  # "up" | "down" | "sideways"
            "magnitude": float,  # 预期涨跌幅 %
            "probability": float  # 0-1
        },
        "medium_term": {...},  # 1月
        "long_term": {...}     # 3月
    },
    "influencing_factors": [
        {"factor": str, "impact": str, "weight": float}
    ],
    "scenarios": [
        {"name": str, "probability": float, "description": str}
    ]
}

# POST /api/ai-signals/risk-monitor
# 风险监控
Request: {
    "portfolio": [
        {"symbol": str, "shares": int, "cost_basis": float}
    ],
    "thresholds": {
        "volatility": float,
        "drawdown": float,
        "sentiment": float
    }
}
Response: {
    "alerts": [
        {
            "symbol": str,
            "risk_type": str,  # "volatility" | "sentiment" | "technical"
            "risk_level": str,  # "high" | "medium" | "low"
            "description": str,
            "recommendation": str,
            "timestamp": str
        }
    ],
    "portfolio_risk_score": float  # 0-100
}
```

### 3. 数据处理模块

#### 历史数据采样

由于AI模型有token限制，需要对5年数据（1254个交易日）进行智能采样：

```python
def sample_historical_data(data: List[Dict], max_points: int = 100) -> List[Dict]:
    """
    采样策略：
    - 最近3个月：每日数据（约63个点）
    - 3-12个月：每周数据（约36个点）
    - 1-5年：每月数据（约48个点）
    总计：约147个点 → 压缩到100个点
    """
```

#### 技术指标计算

```python
def calculate_technical_indicators(data: List[Dict]) -> Dict:
    """
    计算常用技术指标：
    - MA5, MA10, MA20, MA60
    - MACD (12, 26, 9)
    - RSI (14)
    - 布林带 (20, 2)
    - 成交量MA
    """
```

## 数据模型

### StockAnalysis (个股分析)

```python
{
    "symbol": str,
    "name": str,
    "current_price": float,
    "analysis": {
        "macro_environment": str,      # 宏观环境分析
        "industry_trend": str,          # 行业趋势
        "fundamentals": str,            # 基本面分析
        "technical_analysis": str,      # 技术面分析
        "overall_score": float,         # 综合评分 0-100
        "key_metrics": {
            "pe_ratio": float,
            "pb_ratio": float,
            "roe": float,
            "debt_ratio": float
        }
    },
    "data_sources": {
        "historical_days": int,
        "news_count": int,
        "risk_models_used": int
    },
    "timestamp": str,
    "cache_expires": str
}
```

### TradingSignal (交易信号)

```python
{
    "symbol": str,
    "signal": str,                    # "strong_buy" | "buy" | "hold" | "sell" | "strong_sell"
    "confidence": float,              # 0-100
    "current_price": float,
    "support_level": float,
    "resistance_level": float,
    "target_price": float,
    "stop_loss": float,
    "reasoning": {
        "technical": str,
        "sentiment": str,
        "fundamentals": str
    },
    "timestamp": str
}
```

### PortfolioOptimization (组合优化)

```python
{
    "current_analysis": {
        "total_value": float,
        "strengths": List[str],
        "weaknesses": List[str],
        "risk_metrics": {
            "volatility": float,
            "sharpe_ratio": float,
            "max_drawdown": float,
            "beta": float
        }
    },
    "recommendations": [
        {
            "action": str,              # "increase" | "decrease" | "hold" | "exit"
            "symbol": str,
            "current_weight": float,
            "target_weight": float,
            "percentage_change": float,
            "reasoning": str
        }
    ],
    "projected_metrics": {
        "expected_annual_return": float,
        "expected_volatility": float,
        "expected_sharpe": float
    },
    "timestamp": str
}
```

### MarketTrend (市场趋势)

```python
{
    "predictions": {
        "short_term": {
            "period": "1_week",
            "direction": str,           # "up" | "down" | "sideways"
            "magnitude": float,         # 预期涨跌幅 %
            "probability": float        # 0-1
        },
        "medium_term": {
            "period": "1_month",
            "direction": str,
            "magnitude": float,
            "probability": float
        },
        "long_term": {
            "period": "3_months",
            "direction": str,
            "magnitude": float,
            "probability": float
        }
    },
    "influencing_factors": [
        {
            "factor": str,
            "category": str,            # "macro" | "industry" | "sentiment"
            "impact": str,              # "positive" | "negative" | "neutral"
            "weight": float             # 0-1
        }
    ],
    "scenarios": [
        {
            "name": str,
            "probability": float,
            "description": str,
            "expected_return": float
        }
    ],
    "timestamp": str
}
```

### RiskAlert (风险预警)

```python
{
    "symbol": str,
    "risk_type": str,                 # "volatility" | "sentiment" | "technical" | "fundamental"
    "risk_level": str,                # "high" | "medium" | "low"
    "severity_score": float,          # 0-100
    "description": str,
    "indicators": {
        "current_value": float,
        "threshold": float,
        "deviation": float
    },
    "recommendation": str,
    "timestamp": str
}
```

## AI Prompt设计

### 1. 个股分析Prompt模板

```python
STOCK_ANALYSIS_SYSTEM_PROMPT = """你是一位资深的美股投资分析师，拥有20年的市场经验。
请基于提供的多维度数据，对指定股票进行全面分析。

分析框架：
1. 宏观环境分析：当前经济周期、利率环境、政策影响
2. 行业趋势：行业景气度、竞争格局、技术变革
3. 公司基本面：财务健康度、盈利能力、成长性
4. 技术面分析：价格趋势、支撑阻力、技术指标

输出要求：
- 使用JSON格式
- 每个维度100-200字
- 给出0-100的综合评分
- 突出关键风险和机会

今天是{current_date}。"""

STOCK_ANALYSIS_USER_PROMPT = """请分析 {stock_name}({symbol}) 的投资价值。

【历史价格数据】（最近{days}天，采样后{sample_points}个点）
{price_data}

【技术指标】
- MA5: {ma5}, MA20: {ma20}, MA60: {ma60}
- MACD: {macd}
- RSI: {rsi}
- 布林带: 上轨{bb_upper}, 下轨{bb_lower}

【风险指标】
- 波动率: {volatility}
- 夏普比率: {sharpe}
- 最大回撤: {max_drawdown}
- Beta: {beta}

【舆情信息】
{sentiment_summary}

【最新新闻】（最近3条）
{news_summary}

请以JSON格式输出分析结果：
{{
    "macro_environment": "宏观环境分析",
    "industry_trend": "行业趋势分析",
    "fundamentals": "基本面分析",
    "technical_analysis": "技术面分析",
    "overall_score": 75.5,
    "key_metrics": {{
        "growth_potential": 80,
        "risk_level": 45,
        "valuation": 70
    }},
    "summary": "一句话总结"
}}"""
```

### 2. 交易信号Prompt模板

```python
TRADING_SIGNAL_SYSTEM_PROMPT = """你是一位专业的量化交易分析师。
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

TRADING_SIGNAL_USER_PROMPT = """请为 {stock_name}({symbol}) 生成交易信号。

当前价格: ${current_price}

【技术指标】
- 价格趋势: {trend}
- RSI: {rsi} (超买>70, 超卖<30)
- MACD: {macd} (金叉/死叉)
- 布林带位置: {bb_position}
- 成交量: {volume_trend}

【风险信号】
- 波动率: {volatility} (年化)
- 最大回撤: {max_drawdown}
- 近期波动: {recent_volatility}

【舆情】
{sentiment}

【新闻】
{news}

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
```

### 3. 投资组合优化Prompt模板

```python
PORTFOLIO_OPTIMIZATION_SYSTEM_PROMPT = """你是一位资深的投资组合管理专家。
请分析当前投资组合，并提供优化建议。

分析维度：
1. 组合优缺点：集中度、行业分布、风险收益特征
2. 调仓建议：具体增持/减持哪些股票，调整幅度
3. 预期效果：优化后的风险收益指标

输出要求：
- 建议具体可操作（百分比）
- 考虑市场环境和舆情风险
- 使用JSON格式

今天是{current_date}。"""

PORTFOLIO_OPTIMIZATION_USER_PROMPT = """请优化以下投资组合：

【当前持仓】
{portfolio_holdings}

【组合风险指标】
- 年化波动率: {volatility}
- 夏普比率: {sharpe}
- 最大回撤: {max_drawdown}
- Beta: {beta}
- 相关性矩阵: {correlation}

【市场环境】
{market_context}

【个股舆情】
{stocks_sentiment}

请以JSON格式输出：
{{
    "current_analysis": {{
        "strengths": ["优点1", "优点2"],
        "weaknesses": ["缺点1", "缺点2"]
    }},
    "recommendations": [
        {{
            "action": "increase",
            "symbol": "AAPL",
            "current_weight": 20.0,
            "target_weight": 25.0,
            "percentage_change": 5.0,
            "reasoning": "原因说明"
        }}
    ],
    "projected_metrics": {{
        "expected_annual_return": 12.5,
        "expected_volatility": 18.0,
        "expected_sharpe": 0.65
    }}
}}"""
```

### 4. 市场趋势预测Prompt模板

```python
MARKET_TREND_SYSTEM_PROMPT = """你是一位宏观市场分析专家。
请预测市场未来走势，包括短期、中期、长期。

预测维度：
1. 方向：上涨/下跌/震荡
2. 幅度：预期涨跌幅度
3. 概率：发生概率
4. 影响因素：宏观、行业、舆情等
5. 情景分析：不同情景下的概率分布

输出要求：
- 三个时间维度：1周、1月、3月
- 给出概率分布
- 说明关键影响因素
- 使用JSON格式

今天是{current_date}。"""

MARKET_TREND_USER_PROMPT = """请预测市场趋势。

【关注股票】
{watchlist}

【市场指数】
{indices_data}

【宏观指标】
- 利率环境: {interest_rate}
- 通胀水平: {inflation}
- 经济增长: {gdp_growth}

【行业动态】
{industry_trends}

【市场舆情】
{market_sentiment}

【最新新闻】
{market_news}

请以JSON格式输出：
{{
    "predictions": {{
        "short_term": {{
            "period": "1_week",
            "direction": "up",
            "magnitude": 2.5,
            "probability": 0.65
        }},
        "medium_term": {{...}},
        "long_term": {{...}}
    }},
    "influencing_factors": [
        {{
            "factor": "美联储政策",
            "category": "macro",
            "impact": "positive",
            "weight": 0.3
        }}
    ],
    "scenarios": [
        {{
            "name": "乐观情景",
            "probability": 0.4,
            "description": "描述",
            "expected_return": 8.0
        }}
    ]
}}"""
```

### 5. 风险监控Prompt模板

```python
RISK_MONITOR_SYSTEM_PROMPT = """你是一位风险管理专家。
请监控投资组合的风险信号，及时预警。

风险类型：
1. 异常波动：价格剧烈波动
2. 负面舆情：重大负面新闻
3. 技术破位：跌破关键支撑位
4. 基本面恶化：财务指标恶化

风险等级：
- high: 需要立即行动
- medium: 需要密切关注
- low: 正常波动范围

输出要求：
- 识别具体风险类型
- 给出风险等级
- 提供应对建议
- 使用JSON格式

今天是{current_date}。"""

RISK_MONITOR_USER_PROMPT = """请监控以下持仓的风险。

【持仓】
{portfolio}

【风险阈值】
- 波动率阈值: {volatility_threshold}
- 回撤阈值: {drawdown_threshold}
- 舆情阈值: {sentiment_threshold}

【实时数据】
{realtime_data}

【异常信号】
{anomaly_signals}

【舆情监控】
{sentiment_alerts}

请以JSON格式输出风险预警：
{{
    "alerts": [
        {{
            "symbol": "AAPL",
            "risk_type": "volatility",
            "risk_level": "high",
            "severity_score": 85,
            "description": "风险描述",
            "indicators": {{
                "current_value": 0.35,
                "threshold": 0.25,
                "deviation": 0.10
            }},
            "recommendation": "建议减仓20%或设置止损"
        }}
    ],
    "portfolio_risk_score": 65
}}"""
```

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的正式陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性1：AI分析响应结构完整性

*对于任何*股票分析请求，AI响应必须包含所有必需的分析维度（宏观环境、行业趋势、基本面、技术面）。

**验证：需求 US-1.2**

### 属性2：分析输入数据完整性

*对于任何*AI分析请求，输入prompt必须包含所有必需的数据类型（历史价格、技术指标、风险指标、舆情数据）。

**验证：需求 US-1.3**

### 属性3：分析结果结构化输出

*对于任何*分析响应，解析后的结果必须包含评分（0-100范围）、关键指标字典和文字说明。

**验证：需求 US-1.4**

### 属性4：交易信号有效性

*对于任何*交易信号响应，信号值必须是五个有效值之一（strong_buy、buy、hold、sell、strong_sell）。

**验证：需求 US-2.1**

### 属性5：置信度范围有效性

*对于任何*交易信号，置信度评分必须在0到100之间（包含边界）。

**验证：需求 US-2.2**

### 属性6：价格水平存在性

*对于任何*交易信号响应，必须包含支撑位和阻力位的数值。

**验证：需求 US-2.3**

### 属性7：价格建议逻辑一致性

*对于任何*买入信号，止损价必须低于当前价，目标价必须高于当前价；对于卖出信号，止损价必须高于当前价，目标价必须低于当前价。

**验证：需求 US-2.4**

### 属性8：信号依据完整性

*对于任何*交易信号，reasoning字段必须包含技术面、舆情面和基本面三个维度的非空说明。

**验证：需求 US-2.5**

### 属性9：组合分析双向性

*对于任何*投资组合分析，响应必须同时包含优点列表和缺点列表，且两者都不为空。

**验证：需求 US-3.1**

### 属性10：调仓建议可操作性

*对于任何*投资组合优化建议，每个推荐必须包含具体的股票代码和数值化的百分比变化。

**验证：需求 US-3.2, US-3.5**

### 属性11：优化后指标预测

*对于任何*投资组合优化响应，projected_metrics必须包含预期收益、预期风险和夏普比率的数值。

**验证：需求 US-3.3**

### 属性12：优化输入多维度

*对于任何*投资组合优化请求，输入prompt必须包含市场环境数据和舆情数据。

**验证：需求 US-3.4**

### 属性13：趋势预测时间维度完整性

*对于任何*市场趋势预测，响应必须包含短期（1周）、中期（1月）和长期（3月）三个时间维度的预测。

**验证：需求 US-4.1**

### 属性14：趋势预测双要素

*对于任何*时间维度的趋势预测，必须同时包含方向（up/down/sideways）和幅度（百分比数值）。

**验证：需求 US-4.2**

### 属性15：影响因素识别

*对于任何*市场趋势预测，influencing_factors列表必须非空，且每个因素包含类别和影响方向。

**验证：需求 US-4.3**

### 属性16：情景概率归一化

*对于任何*市场趋势预测，所有情景的概率之和必须在0.95到1.05之间（允许浮点误差）。

**验证：需求 US-4.4**

### 属性17：风险监控全覆盖

*对于任何*投资组合风险监控请求，系统必须检查组合中的每一只股票。

**验证：需求 US-5.1**

### 属性18：风险类型识别

*对于任何*检测到的风险，risk_type必须是有效类型之一（volatility、sentiment、technical、fundamental）。

**验证：需求 US-5.2**

### 属性19：风险等级有效性

*对于任何*风险预警，risk_level必须是三个有效值之一（high、medium、low）。

**验证：需求 US-5.3**

### 属性20：风险应对建议

*对于任何*风险预警，recommendation字段必须非空且包含具体的应对建议。

**验证：需求 US-5.4**

### 属性21：阈值可配置性

*对于任何*风险监控请求，系统必须接受并使用自定义的阈值参数（如果提供）。

**验证：需求 US-5.5**

## 错误处理

### AI API错误

```python
class AIAPIError(Exception):
    """AI API调用失败"""
    pass

class AIResponseParseError(Exception):
    """AI响应解析失败"""
    pass

class InsufficientDataError(Exception):
    """数据不足，无法进行分析"""
    pass
```

### 错误处理策略

1. **API超时**：设置30秒超时，超时后返回缓存结果或默认响应
2. **响应解析失败**：尝试提取部分信息，记录错误日志
3. **数据不足**：明确告知用户数据不足，建议等待数据更新
4. **配额限制**：实现请求队列和限流机制
5. **缓存失效**：优雅降级，返回上次成功的分析结果

### 降级策略

```python
def analyze_stock_with_fallback(symbol: str) -> Dict:
    try:
        # 尝试AI分析
        return ai_analyze(symbol)
    except AIAPIError:
        # 降级到基于规则的分析
        return rule_based_analyze(symbol)
    except InsufficientDataError:
        # 返回数据不足提示
        return {"error": "insufficient_data", "message": "需要更多历史数据"}
```

## 测试策略

### 双重测试方法

本功能采用单元测试和基于属性的测试相结合的方法：

- **单元测试**：验证特定示例、边缘情况和错误条件
- **属性测试**：通过随机化验证所有输入的通用属性
- 两者互补且都是全面覆盖所必需的

### 单元测试重点

单元测试应专注于：
- 演示正确行为的特定示例
- 组件之间的集成点
- 边缘情况和错误条件

避免编写过多的单元测试——基于属性的测试处理大量输入的覆盖。

### 基于属性的测试

**测试库**：使用Python的`hypothesis`库进行基于属性的测试

**配置**：
- 每个属性测试最少100次迭代（由于随机化）
- 每个测试必须引用其设计文档属性
- 标签格式：**Feature: ai-trading-signals, Property {number}: {property_text}**

**示例属性测试**：

```python
from hypothesis import given, strategies as st
import pytest

# Feature: ai-trading-signals, Property 4: 交易信号有效性
@given(st.text())
def test_trading_signal_validity(symbol):
    """对于任何股票代码，交易信号必须是五个有效值之一"""
    signal = generate_trading_signal(symbol)
    valid_signals = {"strong_buy", "buy", "hold", "sell", "strong_sell"}
    assert signal["signal"] in valid_signals

# Feature: ai-trading-signals, Property 5: 置信度范围有效性
@given(st.text())
def test_confidence_range(symbol):
    """对于任何交易信号，置信度必须在0-100之间"""
    signal = generate_trading_signal(symbol)
    assert 0 <= signal["confidence"] <= 100

# Feature: ai-trading-signals, Property 16: 情景概率归一化
@given(st.lists(st.text(), min_size=1, max_size=10))
def test_scenario_probabilities_sum(symbols):
    """对于任何市场预测，情景概率之和必须接近1.0"""
    prediction = predict_market_trend(symbols)
    total_prob = sum(s["probability"] for s in prediction["scenarios"])
    assert 0.95 <= total_prob <= 1.05
```

### 集成测试

测试完整的端到端流程：
1. 数据收集 → AI分析 → 响应解析 → 缓存
2. 多个API端点的协同工作
3. 错误处理和降级策略

### 性能测试

- 响应时间：确保<5秒
- 并发处理：测试多个同时请求
- 缓存效果：验证缓存命中率
- API配额管理：测试限流机制

## 性能优化

### 缓存策略

```python
class CacheManager:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1小时
    
    def get_cache_key(self, operation: str, params: Dict) -> str:
        """生成缓存键"""
        return f"{operation}:{hash(json.dumps(params, sort_keys=True))}"
    
    def get(self, key: str) -> Optional[Dict]:
        """获取缓存"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def set(self, key: str, data: Dict):
        """设置缓存"""
        self.cache[key] = (data, time.time())
```

### 数据采样优化

```python
def smart_sample(data: List[Dict], target_points: int = 100) -> List[Dict]:
    """
    智能采样策略：
    - 最近的数据保留更多点（密度更高）
    - 较早的数据采样更稀疏
    - 保留关键转折点
    """
    if len(data) <= target_points:
        return data
    
    # 分段采样
    recent_3m = data[-63:]  # 最近3个月，每日
    recent_9m = data[-252:-63:7]  # 3-12个月，每周
    older = data[:-252:30]  # 1-5年，每月
    
    sampled = older + recent_9m + recent_3m
    
    # 如果还是太多，进一步采样
    if len(sampled) > target_points:
        step = len(sampled) // target_points
        sampled = sampled[::step]
    
    return sampled
```

### API调用优化

```python
class AICallOptimizer:
    def __init__(self):
        self.request_queue = []
        self.rate_limit = 10  # 每分钟10次
        self.last_call_time = 0
    
    async def call_with_rate_limit(self, prompt: str) -> str:
        """带限流的API调用"""
        # 等待满足速率限制
        await self._wait_for_rate_limit()
        
        # 调用API
        response = await self.ai_service.call_api(prompt)
        
        # 更新调用时间
        self.last_call_time = time.time()
        
        return response
    
    async def _wait_for_rate_limit(self):
        """等待满足速率限制"""
        elapsed = time.time() - self.last_call_time
        if elapsed < 60 / self.rate_limit:
            await asyncio.sleep(60 / self.rate_limit - elapsed)
```

## 安全和合规

### 免责声明

所有AI分析结果必须附带明确的免责声明：

```python
DISCLAIMER = """
⚠️ 重要提示：
1. 本分析由AI模型生成，仅供参考，不构成投资建议
2. 投资有风险，入市需谨慎
3. 请根据自身风险承受能力做出投资决策
4. 过往表现不代表未来收益
5. 用户需自行承担投资决策责任
"""
```

### 数据隐私

- 不存储用户的具体持仓数量和成本
- 只缓存分析结果，不缓存个人信息
- 定期清理过期缓存数据

### API密钥管理

```python
# 使用环境变量管理API密钥
STEPFUN_API_KEY = os.getenv('STEPFUN_API_KEY')

# 不在日志中记录完整的API密钥
def log_api_call(key: str):
    masked_key = key[:8] + '...' + key[-4:]
    logger.info(f"API call with key: {masked_key}")
```

## 监控和日志

### 关键指标监控

```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'avg_response_time': 0,
        }
    
    def record_api_call(self, duration: float, cached: bool, error: bool):
        """记录API调用指标"""
        self.metrics['api_calls'] += 1
        if cached:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        if error:
            self.metrics['errors'] += 1
        
        # 更新平均响应时间
        n = self.metrics['api_calls']
        self.metrics['avg_response_time'] = (
            (self.metrics['avg_response_time'] * (n - 1) + duration) / n
        )
```

### 日志记录

```python
import logging

logger = logging.getLogger('ai_signals')
logger.setLevel(logging.INFO)

# 记录关键操作
logger.info(f"Analyzing stock: {symbol}")
logger.info(f"Cache hit: {cache_key}")
logger.error(f"AI API error: {error_message}")
logger.warning(f"Insufficient data for {symbol}")
```

## 部署考虑

### 环境变量

```bash
# AI API配置
STEPFUN_API_KEY=your_stepfun_api_key

# 缓存配置
CACHE_TTL=3600  # 缓存有效期（秒）
MAX_CACHE_SIZE=1000  # 最大缓存条目数

# 性能配置
AI_TIMEOUT=30  # AI API超时时间（秒）
RATE_LIMIT=10  # 每分钟API调用次数限制

# 数据采样配置
MAX_DATA_POINTS=100  # 最大数据点数
```

### 依赖项

```python
# requirements.txt
fastapi>=0.104.0
uvicorn>=0.24.0
requests>=2.31.0
numpy>=1.24.0
pandas>=2.0.0
hypothesis>=6.92.0  # 用于基于属性的测试
pytest>=7.4.0
```

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 未来扩展

### 阶段1（当前）
- 个股分析
- 交易信号
- 投资组合优化
- 市场趋势预测
- 风险监控

### 阶段2（未来）
- 个性化分析（基于用户历史行为）
- 实时推送（WebSocket）
- 回测验证（展示历史信号准确率）
- 多模型对比（集成多个AI模型）
- 社区分享（用户可以分享和讨论分析）

### 阶段3（远期）
- 自动交易建议
- 智能止盈止损
- 风险预算管理
- 情景压力测试
- 机器学习模型训练（基于用户反馈）
