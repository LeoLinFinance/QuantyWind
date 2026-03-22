# 搜索功能与舆情分析解耦优化

## 问题描述

之前每次在市场洞察页面搜索并添加/移除股票时，都会自动触发完整的数据刷新，包括AI舆情分析。这导致：
- ❌ 不必要的AI API调用
- ❌ 浪费token和成本
- ❌ 增加等待时间
- ❌ 用户体验不佳

## 根本原因

在`handleAddStock`和`handleRemoveStock`函数中，调用了`fetchData()`：

```typescript
// 问题代码
const handleAddStock = async (symbol: string) => {
  const res = await axios.post(`/api/watchlist/${symbol}`)
  if (res.data.success) {
    fetchData()  // ❌ 触发完整刷新，包括AI分析
  }
}
```

而`fetchData()`会执行：
```typescript
const fetchData = async () => {
  await fetchBasicData()      // 加载基础数据
  if (useAI) {
    await fetchAIAnalysis()   // ❌ 触发AI舆情分析
  }
}
```

## 解决方案

### 1. 解耦搜索和舆情分析 ✅

修改`handleAddStock`和`handleRemoveStock`，只调用`fetchBasicData()`：

```typescript
// 优化后
const handleAddStock = async (symbol: string) => {
  const res = await axios.post(`/api/watchlist/${symbol}`)
  if (res.data.success) {
    await fetchBasicData()  // ✅ 只刷新基础数据
    setSearchQuery('')
    setSearchResults([])
  }
}

const handleRemoveStock = async (symbol: string) => {
  if (!confirm(`确定要移除 ${symbol} 吗？`)) return
  const res = await axios.delete(`/api/watchlist/${symbol}`)
  if (res.data.success) {
    await fetchBasicData()  // ✅ 只刷新基础数据
  }
}
```

### 2. 添加手动舆情更新按钮 ✅

在页面顶部添加独立的"🤖 更新舆情"按钮：

```typescript
{useAI && (
  <button
    onClick={fetchAIAnalysis}
    disabled={aiLoading}
    className={`px-3 py-1 rounded ${
      aiLoading
        ? 'bg-gray-400 cursor-not-allowed'
        : 'bg-purple-600 hover:bg-purple-700'
    } text-white text-sm`}
    title="手动触发AI舆情分析"
  >
    {aiLoading ? 'AI分析中...' : '🤖 更新舆情'}
  </button>
)}
```

## 优化效果

### 优化前
```
用户搜索股票 → 添加到盯盘 → fetchData()
                              ↓
                    fetchBasicData() + fetchAIAnalysis()
                              ↓
                    ❌ 自动触发AI舆情分析
                    ❌ 消耗token
                    ❌ 增加等待时间
```

### 优化后
```
用户搜索股票 → 添加到盯盘 → fetchBasicData()
                              ↓
                    ✅ 只刷新基础数据（价格、成交量）
                    ✅ 不触发AI分析
                    ✅ 快速响应

用户需要时 → 点击"🤖 更新舆情" → fetchAIAnalysis()
                                    ↓
                          ✅ 主动触发AI分析
                          ✅ 用户可控
```

## 功能说明

### 基础数据刷新（快速）
触发时机：
- ✅ 添加股票
- ✅ 移除股票
- ✅ 点击"刷新"按钮（如果未启用AI）

包含内容：
- 股票价格
- 涨跌幅
- 成交量
- 成交量历史

响应时间：~1-2秒

### AI舆情分析（较慢）
触发时机：
- ✅ 首次加载页面（如果启用AI）
- ✅ 点击"刷新"按钮（如果启用AI）
- ✅ 点击"🤖 更新舆情"按钮
- ✅ 自动刷新定时器（15分钟，如果启用）

包含内容：
- AI舆情分析
- 新闻情感分析
- 市场情绪评估

响应时间：~5-10秒

## 用户操作指南

### 场景1：快速添加股票
1. 在搜索框输入股票代码
2. 点击"搜索"
3. 点击"添加"
4. ✅ 立即看到股票基础信息
5. 舆情列显示"等待分析"
6. 需要时点击"🤖 更新舆情"

### 场景2：批量添加股票
1. 添加多只股票（每次只刷新基础数据）
2. 全部添加完成后
3. 点击一次"🤖 更新舆情"
4. ✅ 一次性更新所有股票的舆情

### 场景3：定期更新
1. 启用"自动刷新"开关
2. 系统每15分钟自动刷新
3. 包括基础数据和AI舆情
4. ✅ 无需手动操作

## 成本节省

### 优化前
假设用户添加10只股票：
- 每次添加触发1次AI分析
- 总计：10次AI API调用
- 成本：10 × token成本

### 优化后
假设用户添加10只股票：
- 添加时不触发AI分析
- 手动点击1次"更新舆情"
- 总计：1次AI API调用
- 成本：1 × token成本
- ✅ 节省90%成本

## 技术细节

### 数据加载策略

#### fetchBasicData()
```typescript
const fetchBasicData = async () => {
  setLoading(true)
  try {
    const [insightRes, stocksRes] = await Promise.all([
      axios.get('/api/market-insight'),
      axios.get('/api/watchlist', { params: { use_ai: false } })  // 关键：use_ai=false
    ])
    setMarketInsight(insightRes.data)
    setWatchlist(stocksRes.data)
    setMarketLastUpdate(new Date())
    setDataLoaded(true)
  } finally {
    setLoading(false)
  }
}
```

#### fetchAIAnalysis()
```typescript
const fetchAIAnalysis = async () => {
  if (!useAI) return  // 如果未启用AI，直接返回
  
  setAiLoading(true)
  try {
    const stocksRes = await axios.get('/api/watchlist', { params: { use_ai: true } })  // use_ai=true
    setWatchlist(stocksRes.data)
  } finally {
    setAiLoading(false)
  }
}
```

### 后端API参数

`/api/watchlist` 接口支持 `use_ai` 参数：
- `use_ai=false`: 只返回基础数据，不调用AI
- `use_ai=true`: 返回包含AI舆情分析的数据

## 最佳实践

### 1. 批量操作
添加多只股票时：
- ✅ 先全部添加完
- ✅ 再点击一次"更新舆情"
- ❌ 不要每添加一只就更新舆情

### 2. 按需更新
- ✅ 只在需要查看舆情时更新
- ✅ 利用缓存，避免频繁更新
- ❌ 不要无意义地频繁点击

### 3. 自动刷新
- ✅ 长时间使用时启用自动刷新
- ✅ 短时间操作时关闭自动刷新
- ✅ 根据使用场景灵活调整

## 监控建议

### 关键指标
1. AI API调用次数
2. 用户操作类型分布
3. 平均响应时间
4. 用户满意度

### 优化目标
- AI API调用减少 > 70%
- 搜索添加响应时间 < 2秒
- 用户投诉减少
- 成本降低

## 总结

通过解耦搜索功能和AI舆情分析：
- ✅ 大幅减少不必要的AI调用
- ✅ 节省token和成本
- ✅ 提升用户体验
- ✅ 保持功能完整性
- ✅ 用户可主动控制

这是一个典型的性能优化案例，在保持功能完整的前提下，通过合理的解耦和用户控制，实现了成本和体验的双重优化。
