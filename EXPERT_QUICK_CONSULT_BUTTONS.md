# 专家快速咨询按钮功能

## 功能概述

在智者论坛的用户输入框下方添加了五个快捷按钮，用户可以快速请求特定专家进行单独分析，无需等待完整的专家讨论流程。

## 功能特点

### 1. 快速访问

用户可以直接点击按钮请求特定专家的分析，无需：
- 开启"开始讨论"开关
- 等待所有专家依次回复
- 受到10分钟冷却时间限制

### 2. 独立调用

每个按钮独立工作：
- 只调用选定的专家
- 不影响其他专家
- 可以连续请求不同专家

### 3. 视觉反馈

- **按钮状态**：显示"分析中..."表示正在请求
- **禁用状态**：请求期间按钮不可点击
- **颜色区分**：不同专家使用不同颜色主题

## 按钮列表

### 1. 📊 选股分析

**专家**：选股分析师
**ID**：`stock_analyst`
**颜色**：蓝色（Blue）
**功能**：根据产业链状况、行业政策与前景、股票标的的近期表现以及财报等，综合推荐5-10只美股和港股

### 2. 🔗 产业链分析

**专家**：产业链分析师
**ID**：`industry_analyst`
**颜色**：紫色（Purple）
**功能**：通过目前已有股票的情况，根据行业政策、产业链拆解，分析产业成本和利润的占比，提供买入和卖出建议

### 3. 📈 短期市场分析

**专家**：市场分析师
**ID**：`market_analyst`
**颜色**：橙色（Orange）
**功能**：根据目前持有股票短期的技术面和价格震荡判断是否需要做适当的减仓或者清仓以规避短期风险

### 4. 💎 长期价值投资分析

**专家**：长期价值投资分析师
**ID**：`value_investor`
**颜色**：绿色（Green）
**功能**：根据持有股票长期的产业情况和长期方向做研判，提供长期持有的建议和支持

### 5. 🌍 经济分析

**专家**：首席经济学家
**ID**：`chief_economist`
**颜色**：靛蓝色（Indigo）
**功能**：研究目前的全球各地区经济形势，收集其他分析师的建议，提供宏观经济视角的投资指导

## 技术实现

### 前端实现

#### 1. 状态管理

```typescript
const [requestingExpert, setRequestingExpert] = useState<string | null>(null)
```

**作用**：跟踪当前正在请求的专家，用于显示加载状态和禁用按钮

#### 2. 请求函数

```typescript
const requestSingleExpert = async (expertId: string) => {
  // 查找专家配置
  const expert = expertConfigs.find(e => e.id === expertId)
  if (!expert) return

  // 设置正在请求的专家
  setRequestingExpert(expertId)

  try {
    // 获取上下文
    let lastNewsSummary = ''
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'kimi') {
        lastNewsSummary = messages[i].content
        break
      }
    }
    
    const context = lastNewsSummary ? `[kimi] ${lastNewsSummary}` : '暂无最新资讯'
    
    // 调用API
    const response = await fetch('http://localhost:8000/api/expert-forum/expert-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        expert_id: expert.id,
        expert_name: expert.name,
        expert_prompt: expert.prompt,
        context: context
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      
      if (data.skipped) {
        // 专家选择不回复
        const skipMessage: Message = {
          id: `system-${Date.now()}`,
          role: 'system',
          content: `${expert.name}认为当前情况无需回复`,
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, skipMessage])
      } else {
        // 添加专家回复
        const expertMessage: Message = {
          id: `expert-${expert.id}-${Date.now()}`,
          role: 'expert',
          expertType: expert.name,
          content: data.analysis,
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, expertMessage])
      }
    }
  } catch (error) {
    console.error(`${expert.name}分析失败:`, error)
    // 显示错误消息
  } finally {
    setRequestingExpert(null)
  }
}
```

#### 3. 按钮UI

```typescript
<button
  onClick={() => requestSingleExpert('stock_analyst')}
  disabled={requestingExpert === 'stock_analyst'}
  className="px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-300 rounded-md hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
>
  {requestingExpert === 'stock_analyst' ? '分析中...' : '📊 选股分析'}
</button>
```

**特点**：
- 动态文本：根据状态显示"分析中..."或专家名称
- 禁用状态：请求期间不可点击
- 视觉反馈：使用不同颜色和图标

### 后端实现

使用现有的 `/api/expert-forum/expert-analysis` 端点，无需修改后端代码。

## UI 布局

```
┌─────────────────────────────────────────────────┐
│ [输入框                              ] [发送]    │
├─────────────────────────────────────────────────┤
│ 快速咨询专家：                                   │
│                                                 │
│ [📊 选股分析] [🔗 产业链分析] [📈 短期市场分析]  │
│ [💎 长期价值投资分析] [🌍 经济分析]              │
├─────────────────────────────────────────────────┤
│ 提示：您的消息会被所有专家看到...                │
└─────────────────────────────────────────────────┘
```

## 用户体验流程

### 正常流程

```
1. 用户点击"📊 选股分析"按钮
   ↓
2. 按钮显示"分析中..."并禁用
   ↓
3. 发送API请求到后端
   ↓
4. 等待专家分析（30-60秒）
   ↓
5. 收到专家回复
   ↓
6. 在对话框中显示回复
   ↓
7. 按钮恢复正常状态
```

### 专家选择不回复

```
1. 用户点击按钮
   ↓
2. 发送请求
   ↓
3. 专家判断无需回复
   ↓
4. 显示系统消息："选股分析师认为当前情况无需回复"
   ↓
5. 按钮恢复正常状态
```

### 请求失败

```
1. 用户点击按钮
   ↓
2. 发送请求
   ↓
3. 网络错误或超时
   ↓
4. 显示系统消息："选股分析师分析失败，请稍后重试"
   ↓
5. 按钮恢复正常状态
```

## 与"开始讨论"的区别

| 特性 | 快捷按钮 | 开始讨论 |
|------|---------|---------|
| 调用方式 | 单个专家 | 所有专家 |
| 冷却时间 | 无限制 | 10分钟 |
| 调用顺序 | 即时 | 依次调用 |
| 等待时间 | 30-60秒 | 5-10分钟 |
| 使用场景 | 快速咨询 | 全面讨论 |

## 使用场景

### 1. 快速决策

用户需要特定专家的意见来做出快速决策：
- 看到新闻后想了解短期市场影响 → 点击"短期市场分析"
- 考虑买入新股票 → 点击"选股分析"
- 评估长期持有价值 → 点击"长期价值投资分析"

### 2. 针对性咨询

用户只需要某个领域的专业意见：
- 只关心产业链分析 → 点击"产业链分析"
- 只关心宏观经济 → 点击"经济分析"

### 3. 补充分析

在完整讨论后，用户想要某个专家的补充意见：
- 所有专家讨论完成
- 用户对某个领域还有疑问
- 点击对应按钮获取补充分析

## 优势

### 1. 提高效率

- **节省时间**：无需等待所有专家回复
- **即时响应**：点击即可获得分析
- **无冷却限制**：可以随时请求

### 2. 灵活性

- **按需咨询**：只请求需要的专家
- **多次请求**：可以连续请求不同专家
- **独立操作**：不影响其他功能

### 3. 用户友好

- **清晰标识**：图标和颜色区分
- **状态反馈**：显示加载状态
- **错误处理**：友好的错误提示

## 注意事项

### 1. API限流

虽然没有前端冷却限制，但后端可能有API限流：
- 建议在请求间添加适当延迟
- 避免短时间内大量请求
- 监控API使用量

### 2. 上下文一致性

快捷按钮使用与"开始讨论"相同的上下文：
- 最后一次资讯总结
- 当前持仓信息
- 对话历史（通过聊天服务）

### 3. 用户教育

需要让用户了解：
- 快捷按钮的作用
- 与"开始讨论"的区别
- 何时使用哪种方式

## 未来优化

### 1. 智能推荐

根据用户行为推荐专家：
```typescript
// 分析用户最近的问题
if (userQuestion.includes('买入')) {
  // 高亮"选股分析"按钮
}
```

### 2. 批量请求

允许用户选择多个专家：
```typescript
<Checkbox>选股分析</Checkbox>
<Checkbox>产业链分析</Checkbox>
<Button>批量咨询</Button>
```

### 3. 历史记录

显示每个专家的最后回复时间：
```typescript
<button>
  📊 选股分析
  <span className="text-xs">2小时前</span>
</button>
```

### 4. 快捷键支持

为每个按钮添加快捷键：
- Ctrl+1: 选股分析
- Ctrl+2: 产业链分析
- Ctrl+3: 短期市场分析
- Ctrl+4: 长期价值投资分析
- Ctrl+5: 经济分析

### 5. 自定义按钮

允许用户自定义快捷按钮：
- 选择显示哪些专家
- 调整按钮顺序
- 设置按钮颜色

## 测试建议

### 功能测试

- [ ] 点击每个按钮都能正常请求
- [ ] 按钮在请求期间正确禁用
- [ ] 专家回复正确显示在对话框
- [ ] 专家选择不回复时显示系统消息
- [ ] 请求失败时显示错误消息

### 性能测试

- [ ] 单个请求响应时间 < 60秒
- [ ] 连续请求不会导致卡顿
- [ ] 多个按钮同时点击的处理

### UI测试

- [ ] 按钮颜色和图标正确显示
- [ ] 按钮在不同屏幕尺寸下正常显示
- [ ] 加载状态文本正确切换
- [ ] 禁用状态视觉效果明显

### 边界测试

- [ ] 无网络连接时的处理
- [ ] API超时的处理
- [ ] 专家配置缺失的处理
- [ ] 快速连续点击的处理

## 总结

快速咨询按钮功能为用户提供了更灵活、高效的专家咨询方式。用户可以根据自己的需求快速获取特定专家的分析，无需等待完整的讨论流程。这大大提升了智者论坛的实用性和用户体验。
