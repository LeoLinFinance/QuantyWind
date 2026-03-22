# 自动刷新功能归因分析

## 问题描述
系统每15分钟自动刷新市场洞察数据，导致大量token消耗。用户希望只在手动点击刷新按钮时才更新数据。

## 归因分析

### 1. 自动刷新触发位置

#### 前端触发点
在以下三个页面中都存在自动刷新定时器：

**MarketInsightPage.tsx (第137-145行)**
```typescript
useEffect(() => {
  if (!autoRefreshEnabled) return

  const interval = setInterval(() => {
    console.log('市场洞察页面：自动刷新触发')
    fetchData()
  }, 15 * 60 * 1000) // 15分钟

  return () => clearInterval(interval)
}, [autoRefreshEnabled])
```

**RiskAnalysisPage.tsx (第238-246行)**
```typescript
useEffect(() => {
  if (!autoRefreshEnabled) return

  const interval = setInterval(() => {
    console.log('风险分析页面：自动刷新触发')
    fetchData()
  }, 15 * 60 * 1000) // 15分钟

  return () => clearInterval(interval)
}, [autoRefreshEnabled])
```

**SentimentMapPage.tsx (第112-120行)**
```typescript
useEffect(() => {
  if (!autoRefreshEnabled) return

  const interval = setInterval(() => {
    console.log('舆情地图页面：自动刷新触发')
    fetchData()
  }, 15 * 60 * 1000) // 15分钟

  return () => clearInterval(interval)
}, [autoRefreshEnabled])
```

### 2. 全局状态管理

**DataContext.tsx**
- `autoRefreshEnabled`: 控制自动刷新开关的全局状态
- 默认值：`false`（已经是关闭状态）
- 用户可以通过页面右上角的iOS风格开关切换

### 3. Token消耗来源

每次刷新会调用以下API：

#### 市场洞察页面
1. `/api/market-insight` - 获取市场整体洞察（包含AI分析）
2. `/api/watchlist?use_ai=true` - 获取盯盘股票列表（包含AI舆情分析）

#### 后端服务
**market_service.py**
- `get_latest_insight()`: 获取指数数据和市场情绪
- `get_watchlist(use_ai=True)`: 
  - 调用 `yahoo_api.get_multiple_quotes()` 获取股票数据
  - 调用 `ai_service.batch_analyze_sentiment()` 进行AI舆情分析（主要token消耗点）

### 4. 当前问题

虽然自动刷新开关默认是关闭的，但可能存在以下情况：
1. 用户不小心打开了自动刷新开关
2. 没有后端缓存机制，每次刷新都会重新调用AI API
3. 没有数据过期时间控制，即使数据很新也会重新获取

## 优化方案

### 方案1：后端缓存机制（推荐）
在后端实现缓存层，避免频繁调用AI API：
- 缓存市场洞察数据（有效期：5分钟）
- 缓存股票舆情分析（有效期：15分钟）
- 只有缓存过期时才调用AI API

### 方案2：前端智能刷新
- 检查数据更新时间，如果距离上次更新不足5分钟，直接使用缓存数据
- 只在用户主动点击刷新按钮时强制更新

### 方案3：分离AI分析
- 基础数据（价格、涨跌幅）实时更新
- AI舆情分析按需加载，用户点击"更新舆情"按钮时才调用

## 实施建议

1. **立即实施**：后端缓存机制（方案1）
2. **已实现**：前端已有"启用AI舆情分析"开关和独立的"更新舆情"按钮
3. **用户教育**：确保自动刷新开关默认关闭，并提示用户合理使用

## 预期效果

- Token消耗减少80%以上
- 响应速度提升（使用缓存数据）
- 用户体验改善（按需加载）
