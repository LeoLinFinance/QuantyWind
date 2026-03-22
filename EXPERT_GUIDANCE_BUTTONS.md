# 专家引导按钮功能

## 功能概述

在智者论坛中，特定专家回复后会自动显示引导按钮，帮助用户快速跳转到相关功能页面，提升用户体验和功能发现性。

## 引导规则

### 1. 选股分析师

**触发条件**：当"选股分析师"发表回复后

**引导内容**：
- 提示文本：💡 如果有任何看中的股票信息，可以点击下方按钮添加心仪股票，我们会负责帮你盯盘了解动向
- 按钮文本：前往市场盯盘 →
- 跳转页面：`/market-insight`（市场盯盘页）

**使用场景**：选股分析师推荐了股票后，用户可以直接前往市场盯盘页添加关注的股票

### 2. 长期价值投资分析师

**触发条件**：当"长期价值投资分析师"发表回复后

**引导内容**：
- 提示文本：💡 如果想进一步了解关注股票的风险，可以点击下方按钮用更专业的数据了解你的股票风险
- 按钮文本：查看风险分析 →
- 跳转页面：`/risk-analysis`（风险分析页）

**使用场景**：长期价值投资分析师分析持仓后，用户可以前往风险分析页查看详细的风险指标

### 3. 首席经济学家

**触发条件**：当"首席经济学家"发表回复后

**引导内容**：
- 提示文本：💡 如果想了解世界各地区的舆情风险，可以点击下方按钮前往洞察
- 按钮文本：查看舆情地图 →
- 跳转页面：`/sentiment-map`（舆情地图页）

**使用场景**：首席经济学家分析宏观经济形势后，用户可以前往舆情地图查看全球市场情绪

## 技术实现

### 前端实现

**文件**：`src/pages/ExpertForumPage.tsx`

#### 1. 导入路由钩子

```typescript
import { useNavigate } from 'react-router-dom'
```

#### 2. 引导信息映射函数

```typescript
const getExpertGuidance = (expertType: string | undefined) => {
  if (!expertType) return null
  
  const guidanceMap: Record<string, { text: string; buttonText: string; route: string }> = {
    '选股分析师': {
      text: '如果有任何看中的股票信息，可以点击下方按钮添加心仪股票，我们会负责帮你盯盘了解动向',
      buttonText: '前往市场盯盘',
      route: '/market-insight'
    },
    '长期价值投资分析师': {
      text: '如果想进一步了解关注股票的风险，可以点击下方按钮用更专业的数据了解你的股票风险',
      buttonText: '查看风险分析',
      route: '/risk-analysis'
    },
    '首席经济学家': {
      text: '如果想了解世界各地区的舆情风险，可以点击下方按钮前往洞察',
      buttonText: '查看舆情地图',
      route: '/sentiment-map'
    }
  }
  
  return guidanceMap[expertType] || null
}
```

#### 3. 消息渲染中添加引导按钮

```typescript
messages.map(message => {
  const guidance = message.role === 'expert' ? getExpertGuidance(message.expertType) : null
  
  return (
    <div className={`p-4 rounded-lg border-2 ${getRoleColor(message.role)}`}>
      {/* 消息内容 */}
      <div className="text-sm text-gray-800 whitespace-pre-wrap">
        {message.content}
      </div>
      
      {/* 专家引导按钮 */}
      {guidance && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-600 mb-2">
            💡 {guidance.text}
          </p>
          <button
            onClick={() => navigate(guidance.route)}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
          >
            {guidance.buttonText} →
          </button>
        </div>
      )}
    </div>
  )
})
```

## UI 设计

### 视觉样式

- **分隔线**：引导区域与消息内容之间有灰色分隔线
- **图标**：使用 💡 灯泡图标表示提示
- **文本颜色**：灰色文本（`text-gray-600`）表示辅助信息
- **按钮样式**：蓝色背景（`bg-blue-600`），悬停时变深（`hover:bg-blue-700`）
- **箭头符号**：按钮文本后添加 → 符号，增强跳转感

### 布局

```
┌─────────────────────────────────────┐
│ 专家名称                    时间戳   │
├─────────────────────────────────────┤
│                                     │
│ 专家回复内容...                      │
│                                     │
├─────────────────────────────────────┤ ← 分隔线
│ 💡 引导文本...                       │
│                                     │
│ ┌─────────────────┐                │
│ │ 按钮文本 →      │                │
│ └─────────────────┘                │
└─────────────────────────────────────┘
```

## 用户体验优势

1. **上下文相关**：引导按钮只在相关专家回复后出现，避免信息过载
2. **即时行动**：用户可以立即根据专家建议采取行动
3. **功能发现**：帮助用户发现和使用系统的其他功能
4. **流畅导航**：一键跳转，无需手动查找页面
5. **视觉清晰**：使用图标和颜色区分引导信息

## 扩展性

### 添加新的专家引导

如果需要为其他专家添加引导按钮，只需在 `guidanceMap` 中添加新的映射：

```typescript
const guidanceMap: Record<string, { text: string; buttonText: string; route: string }> = {
  // 现有映射...
  
  '新专家名称': {
    text: '引导文本',
    buttonText: '按钮文本',
    route: '/目标路由'
  }
}
```

### 支持多个按钮

如果需要在一个专家回复后显示多个按钮，可以修改数据结构：

```typescript
type Guidance = {
  text: string
  buttons: Array<{ text: string; route: string }>
}
```

### 支持外部链接

如果需要跳转到外部链接，可以添加 `external` 标记：

```typescript
{
  text: '查看更多资讯',
  buttonText: '访问官网',
  route: 'https://example.com',
  external: true
}
```

## 注意事项

1. **专家名称匹配**：引导按钮依赖于精确的专家名称匹配，修改专家名称时需要同步更新 `guidanceMap`
2. **路由有效性**：确保 `route` 中的路径在应用的路由配置中存在
3. **历史消息**：引导按钮会在历史消息中保留，用户刷新页面后仍然可见
4. **响应式设计**：按钮在移动设备上也能正常显示和点击

## 测试建议

1. 启动应用，进入智者论坛
2. 开启"接收资讯"和"开始讨论"
3. 等待各个专家回复
4. 验证以下内容：
   - 选股分析师回复后显示"前往市场盯盘"按钮
   - 长期价值投资分析师回复后显示"查看风险分析"按钮
   - 首席经济学家回复后显示"查看舆情地图"按钮
   - 其他专家回复后不显示引导按钮
5. 点击按钮，验证能正确跳转到目标页面
6. 刷新页面，验证历史消息中的按钮仍然可用
