# 混合模型策略：精细化成本优化

## 策略概述

采用混合模型策略，根据不同功能的需求选择合适的模型：
- **AI智能分析**: 使用32k模型（需要大上下文）
- **其他功能**: 使用8k模型（足够使用）

## 模型分配

### 使用32k模型的功能 ✅

#### 1. AI智能分析 (`analyze_stock`)
**原因**: 需要处理大量上下文信息
- 历史价格数据（365天）
- 技术指标（MA、MACD、RSI、布林带）
- 风险指标（波动率、回撤、夏普比率等）
- 舆情信息（新闻 + 情感分析）
- 在线研究（Kimi Code搜索结果）

**Token估算**: 5000-7000 tokens
**模型**: `step-1v-32k`
**调用频率**: 低（用户主动触发）

### 使用8k模型的功能 ✅

#### 1. 舆情分析 (`analyze_sentiment`)
**原因**: 输入输出都很简短
- 输入：股票代码 + 3条新闻摘要
- 输出：30字以内的舆情评估

**Token估算**: 500-800 tokens
**模型**: `step-1v-8k`
**调用频率**: 高（批量分析盯盘列表）

#### 2. 交易信号 (`generate_trading_signal`)
**原因**: 输入适中，不需要大上下文
- 输入：技术指标 + 风险指标 + 舆情
- 输出：买卖信号 + 价格水平

**Token估算**: 2000-3000 tokens
**模型**: `step-1v-8k`
**调用频率**: 中（用户主动触发）

#### 3. 在线研究 (`kimi_research`)
**原因**: Kimi的8k模型足够
- 输入：研究问题
- 输出：研究结果摘要（限制500字）

**Token估算**: 2000-3000 tokens
**模型**: `moonshot-v1-8k`
**调用频率**: 低（AI分析时自动调用）

## 实现方式

### 1. AI Service 修改 ✅

在`_call_stepfun`方法中添加`model`参数：

```python
def _call_stepfun(self, system_prompt: str, user_prompt: str, 
                  max_tokens: int = 100, model: str = None) -> str:
    """
    调用阶跃星辰API
    
    Args:
        model: 指定模型（如果为None则使用默认的8k模型）
    """
    use_model = model if model else self.stepfun_model  # 默认8k
    # ...
```

### 2. AI Signals Service 修改 ✅

在`analyze_stock`中指定使用32k模型：

```python
# AI智能分析使用32k模型
ai_response = self.ai_service._call_stepfun(
    system_prompt, 
    user_prompt, 
    max_tokens=1000,
    model='step-1v-32k'  # 明确指定32k
)
```

其他功能不指定model参数，自动使用默认的8k模型。

## 成本对比

### 假设场景
- 每天100次舆情分析（8k）
- 每天20次交易信号（8k）
- 每天5次AI智能分析（32k）
- 每天5次在线研究（8k）

### 成本计算

#### 方案1：全部使用32k
```
阶跃星辰:
- 舆情: 100次 × 800 tokens × ¥0.005/1K = ¥0.40
- 交易: 20次 × 2500 tokens × ¥0.005/1K = ¥0.25
- 分析: 5次 × 6000 tokens × ¥0.005/1K = ¥0.15
总计: ¥0.80/天 = ¥24/月

Kimi:
- 研究: 5次 × 2500 tokens × ¥0.024/1K = ¥0.30
总计: ¥0.30/天 = ¥9/月

合计: ¥33/月
```

#### 方案2：全部使用8k
```
阶跃星辰:
- 舆情: 100次 × 800 tokens × ¥0.001/1K = ¥0.08
- 交易: 20次 × 2500 tokens × ¥0.001/1K = ¥0.05
- 分析: 5次 × 6000 tokens × ¥0.001/1K = ¥0.03
总计: ¥0.16/天 = ¥4.8/月

Kimi:
- 研究: 5次 × 2500 tokens × ¥0.012/1K = ¥0.15
总计: ¥0.15/天 = ¥4.5/月

合计: ¥9.3/月
```

#### 方案3：混合策略（推荐）✅
```
阶跃星辰:
- 舆情: 100次 × 800 tokens × ¥0.001/1K = ¥0.08
- 交易: 20次 × 2500 tokens × ¥0.001/1K = ¥0.05
- 分析: 5次 × 6000 tokens × ¥0.005/1K = ¥0.15  ← 使用32k
总计: ¥0.28/天 = ¥8.4/月

Kimi:
- 研究: 5次 × 2500 tokens × ¥0.012/1K = ¥0.15
总计: ¥0.15/天 = ¥4.5/月

合计: ¥12.9/月
```

### 成本对比总结

| 方案 | 月成本 | vs全32k | vs全8k | 功能完整性 |
|------|--------|---------|--------|-----------|
| 全部32k | ¥33 | - | +255% | ✅ 完整 |
| 全部8k | ¥9.3 | -72% | - | ⚠️ AI分析可能截断 |
| 混合策略 | ¥12.9 | -61% | +39% | ✅ 完整 |

**结论**: 混合策略在保证功能完整性的前提下，相比全32k节省61%成本。

## 优势分析

### 1. 成本优化 ✅
- 高频功能（舆情分析）使用便宜的8k模型
- 低频功能（AI分析）使用32k模型保证质量
- 整体成本降低61%

### 2. 功能保障 ✅
- AI智能分析不会因为上下文限制而截断
- 可以包含完整的历史数据和在线研究
- 分析质量不受影响

### 3. 灵活扩展 ✅
- 可以根据实际使用情况调整策略
- 新功能可以灵活选择模型
- 易于监控和优化

## 监控指标

### 1. Token使用统计
```python
# 按功能统计token使用
{
  "sentiment_analysis": {
    "model": "step-1v-8k",
    "avg_tokens": 750,
    "daily_calls": 100
  },
  "trading_signal": {
    "model": "step-1v-8k",
    "avg_tokens": 2500,
    "daily_calls": 20
  },
  "ai_analysis": {
    "model": "step-1v-32k",
    "avg_tokens": 6000,
    "daily_calls": 5
  }
}
```

### 2. 成本追踪
- 每日成本
- 每功能成本占比
- 成本趋势

### 3. 质量监控
- AI分析是否被截断
- 用户满意度
- 错误率

## 日志示例

### 启动日志
```
✅ AI服务初始化: 使用阶跃星辰模型 step-1v-8k (默认)
✅ Kimi Research Service initialized (moonshot-v1-8k)
```

### 运行日志
```
# 舆情分析（8k）
🤖 调用阶跃星辰API: 模型=step-1v-8k, max_tokens=100
✅ AI响应成功: 28 字符

# 交易信号（8k）
🤖 调用阶跃星辰API: 模型=step-1v-8k, max_tokens=800
✅ AI响应成功: 450 字符

# AI智能分析（32k）
🤖 调用阶跃星辰API: 模型=step-1v-32k, max_tokens=1000
✅ AI响应成功: 620 字符
```

## 配置说明

### 环境变量
```bash
# .env文件
STEPFUN_MODEL=step-1v-8k  # 默认使用8k模型
```

### 代码配置
```python
# ai_service.py
self.stepfun_model = os.getenv('STEPFUN_MODEL', 'step-1v-8k')  # 默认8k

# ai_signals_service.py - analyze_stock
ai_response = self.ai_service._call_stepfun(
    system_prompt, 
    user_prompt, 
    max_tokens=1000,
    model='step-1v-32k'  # AI分析明确使用32k
)
```

## 未来优化

### 1. 动态模型选择
根据输入大小自动选择模型：
```python
def smart_model_selection(input_tokens: int) -> str:
    if input_tokens > 6000:
        return 'step-1v-32k'
    else:
        return 'step-1v-8k'
```

### 2. 成本预算控制
设置每日/每月成本上限：
```python
if daily_cost > budget_limit:
    # 降级到8k模型或限制调用
    pass
```

### 3. A/B测试
对比不同模型的效果：
- 分析质量
- 用户满意度
- 成本效益比

## 总结

混合模型策略是一个平衡成本和质量的最优方案：
- ✅ 保证核心功能（AI分析）的质量
- ✅ 降低高频功能（舆情）的成本
- ✅ 整体成本降低61%
- ✅ 功能完整性不受影响
- ✅ 灵活可扩展

这是一个精细化的成本优化策略，在实际运营中可以根据数据持续优化。
