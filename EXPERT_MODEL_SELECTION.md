# 专家模型选择功能

## 功能概述

在专家配置中添加了模型选择功能，允许为每个专家单独配置使用的AI模型。用户可以根据不同专家的需求选择最合适的模型。

## 可用模型

### 1. step-1-8k（快速，8k上下文）
- **上下文窗口**：8,000 tokens
- **适用场景**：简单快速的分析
- **响应速度**：最快（15-20秒）
- **成本**：最低
- **推荐用于**：快速市场评论、简单问答

### 2. step-1-32k（标准，32k上下文）
- **上下文窗口**：32,000 tokens
- **适用场景**：一般对话
- **响应速度**：快（20-30秒）
- **成本**：低
- **推荐用于**：日常分析、中等长度对话

### 3. step-1-256k（超长，256k上下文）
- **上下文窗口**：256,000 tokens
- **适用场景**：长对话和深度分析
- **响应速度**：中等（40-50秒）
- **成本**：中等
- **推荐用于**：深度研究、长期跟踪、复杂分析
- **默认模型**：所有专家默认使用此模型

### 4. step-3.5-flash（极速）
- **特点**：最快响应速度
- **适用场景**：需要即时反馈的场景
- **响应速度**：极快（10-15秒）
- **成本**：低
- **推荐用于**：快速咨询、实时分析

### 5. step-3（高级）
- **特点**：更强的推理能力
- **适用场景**：复杂问题分析
- **响应速度**：中等（30-40秒）
- **成本**：较高
- **推荐用于**：复杂策略制定、深度推理

### 6. step-r1-v-mini（推理）
- **特点**：专注于逻辑推理
- **适用场景**：需要严密逻辑的分析
- **响应速度**：中等（30-40秒）
- **成本**：中等
- **推荐用于**：风险评估、逻辑分析

## 功能实现

### 后端实现

#### 1. 数据模型

**ExpertConfig**：
```python
class ExpertConfig(BaseModel):
    id: str
    name: str
    prompt: str
    model: Optional[str] = None  # 可选的模型参数
```

#### 2. API修改

**ExpertAnalysisRequest**：
```python
class ExpertAnalysisRequest(BaseModel):
    expert_id: str
    expert_name: str
    expert_prompt: str
    context: str
    model: Optional[str] = None  # 添加模型参数
```

#### 3. 服务层

**get_expert_analysis**：
```python
async def get_expert_analysis(
    self,
    expert_id: str,
    expert_name: str,
    expert_prompt: str,
    context: str,
    model: str = None  # 接受模型参数
) -> Dict:
    # 传递模型参数到API调用
    analysis = await self._call_stepfun_for_analysis(
        expert_id,
        expert_prompt,
        full_query,
        model  # 传递模型
    )
```

**_call_stepfun_for_analysis**：
```python
def _call_stepfun_for_analysis(
    self,
    expert_id: str,
    system_prompt: str,
    user_query: str,
    model: str = None  # 接受模型参数
) -> str:
    # 确定使用的模型
    selected_model = model if model else self.stepfun_model
    
    # 使用选定的模型
    response = client.chat.completions.create(
        model=selected_model,
        messages=[...]
    )
```

### 前端实现

#### 1. 数据结构

**ExpertConfig接口**：
```typescript
interface ExpertConfig {
  id: string
  name: string
  prompt: string
  model?: string  // 可选的模型字段
}
```

#### 2. 模型选项

```typescript
const AVAILABLE_MODELS = [
  { value: 'step-1-8k', label: 'Step-1-8k (快速，8k上下文)', description: '适合简单快速的分析' },
  { value: 'step-1-32k', label: 'Step-1-32k (标准，32k上下文)', description: '适合一般对话' },
  { value: 'step-1-256k', label: 'Step-1-256k (超长，256k上下文)', description: '适合长对话和深度分析' },
  { value: 'step-3.5-flash', label: 'Step-3.5-Flash (极速)', description: '最快响应速度' },
  { value: 'step-3', label: 'Step-3 (高级)', description: '更强的推理能力' },
  { value: 'step-r1-v-mini', label: 'Step-R1-V-Mini (推理)', description: '专注于逻辑推理' }
]
```

#### 3. UI组件

**模型选择下拉框**：
```typescript
<select
  value={editingExpert.model || 'step-1-256k'}
  onChange={(e) => setEditingExpert({ ...editingExpert, model: e.target.value })}
  className="w-full p-2 border rounded-md text-sm"
>
  {AVAILABLE_MODELS.map(model => (
    <option key={model.value} value={model.value}>
      {model.label} - {model.description}
    </option>
  ))}
</select>
```

**显示当前模型**：
```typescript
<p className="text-xs text-gray-500 mb-1">
  模型: {expert.model || 'step-1-256k'}
</p>
```

#### 4. API调用

```typescript
const response = await fetch('http://localhost:8000/api/expert-forum/expert-analysis', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    expert_id: expert.id,
    expert_name: expert.name,
    expert_prompt: expert.prompt,
    context: context,
    model: expert.model  // 传递模型参数
  })
})
```

## 使用指南

### 配置专家模型

1. 点击"配置专家"按钮
2. 选择要编辑的专家，点击"编辑"
3. 在"模型选择"下拉框中选择合适的模型
4. 编辑提示词（如需要）
5. 点击"保存"

### 模型选择建议

#### 选股分析师
**推荐模型**：step-1-256k 或 step-3
- 需要分析大量股票信息
- 需要参考历史讨论
- 需要详细的推荐理由

#### 产业链分析师
**推荐模型**：step-1-256k 或 step-3
- 需要深入的产业链分析
- 需要大量上下文信息
- 需要复杂的推理

#### 市场分析师
**推荐模型**：step-3.5-flash 或 step-1-32k
- 需要快速响应
- 技术分析相对简单
- 实时性要求高

#### 长期价值投资分析师
**推荐模型**：step-1-256k 或 step-3
- 需要长期历史数据
- 需要深度分析
- 需要参考完整对话历史

#### 首席经济学家
**推荐模型**：step-1-256k 或 step-r1-v-mini
- 需要宏观视角
- 需要逻辑推理
- 需要综合所有信息

## 性能对比

| 模型 | 响应时间 | 上下文 | 成本 | 推理能力 |
|------|---------|--------|------|---------|
| step-1-8k | 15-20秒 | 8k | ⭐ | ⭐⭐ |
| step-1-32k | 20-30秒 | 32k | ⭐⭐ | ⭐⭐⭐ |
| step-1-256k | 40-50秒 | 256k | ⭐⭐⭐ | ⭐⭐⭐ |
| step-3.5-flash | 10-15秒 | - | ⭐⭐ | ⭐⭐⭐ |
| step-3 | 30-40秒 | - | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| step-r1-v-mini | 30-40秒 | - | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 成本优化建议

### 1. 根据场景选择模型

**快速咨询**：使用 step-3.5-flash 或 step-1-8k
- 节省成本
- 快速响应
- 适合简单问题

**深度分析**：使用 step-1-256k 或 step-3
- 更好的质量
- 完整的上下文
- 适合复杂问题

### 2. 混合使用

不同专家使用不同模型：
- 市场分析师：step-3.5-flash（快速）
- 选股分析师：step-1-256k（深度）
- 产业链分析师：step-3（推理）

### 3. 动态调整

根据对话长度调整：
- 对话开始：使用较小模型
- 对话深入：切换到大模型
- 快速咨询：使用flash模型

## 注意事项

### 1. 模型兼容性

所有模型都支持相同的API接口，切换模型不需要修改提示词。

### 2. 上下文限制

- 8k模型：约40条消息
- 32k模型：约160条消息
- 256k模型：约1280条消息

超过限制会导致错误，建议使用对话总结功能。

### 3. 响应时间

不同模型的响应时间不同，已设置70秒超时，足够所有模型使用。

### 4. 成本监控

建议监控不同模型的使用情况和成本：
```python
logger.info(f"模型: {selected_model}, Token使用: {total_tokens}, 成本: ${cost:.4f}")
```

## 测试建议

### 1. 功能测试

- [ ] 配置专家模型
- [ ] 保存配置
- [ ] 使用不同模型调用专家
- [ ] 验证模型参数正确传递

### 2. 性能测试

- [ ] 测试不同模型的响应时间
- [ ] 验证超时设置是否合适
- [ ] 检查用户体验

### 3. 成本测试

- [ ] 记录不同模型的token使用
- [ ] 计算成本差异
- [ ] 优化模型选择

## 未来优化

### 1. 智能模型推荐

根据问题复杂度自动推荐模型：
```typescript
function recommendModel(question: string, historyLength: number): string {
  if (historyLength < 10 && question.length < 100) {
    return 'step-3.5-flash'
  } else if (historyLength > 50) {
    return 'step-1-256k'
  } else {
    return 'step-1-32k'
  }
}
```

### 2. 模型性能统计

显示每个模型的使用统计：
- 平均响应时间
- 成功率
- 用户满意度

### 3. A/B测试

对比不同模型的效果：
- 回复质量
- 用户反馈
- 成本效益

### 4. 自定义模型参数

允许配置更多参数：
- temperature
- max_tokens
- top_p

## 总结

模型选择功能为智者论坛提供了更大的灵活性：

✅ **优势**：
- 根据需求选择最合适的模型
- 优化成本和性能平衡
- 提供更好的用户体验

💡 **建议**：
- 默认使用 step-1-256k 保证质量
- 快速咨询使用 step-3.5-flash
- 复杂推理使用 step-3 或 step-r1-v-mini
- 定期评估和优化模型选择

这个功能让用户可以根据实际需求灵活配置每个专家，在成本、速度和质量之间找到最佳平衡！
