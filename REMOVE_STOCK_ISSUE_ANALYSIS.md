# 删除股票导致舆情消失问题归因分析

## 问题描述

用户删除一只股票时，所有其他股票的舆情提示信息都会消失，体验很差。

## 问题归因

### 根本原因

**删除股票后调用了`fetchBasicData(false)`，导致整个列表被重新获取，但只获取基础数据（`use_ai: false`），覆盖了原有的舆情信息。**

### 问题链路

1. 用户点击"移除"按钮
2. 调用`handleRemoveStock(symbol)`
3. 后端删除股票成功
4. 前端调用`fetchBasicData(false)`
5. `fetchBasicData`调用`/api/watchlist?use_ai=false`
6. 返回的数据中所有股票的`sentiment`字段都是`'暂无舆情数据'`
7. `setWatchlist(stocksRes.data)`覆盖了原有数据
8. **所有股票的舆情信息丢失**

### 代码位置

**src/pages/MarketInsightPage.tsx (第176-187行)**
```typescript
const handleRemoveStock = async (symbol: string) => {
  if (!confirm(`确定要移除 ${symbol} 吗？`)) return
  try {
    const res = await axios.delete(`/api/watchlist/${symbol}`)
    if (res.data.success) {
      // 问题所在：调用fetchBasicData会覆盖所有舆情数据
      await fetchBasicData(false)
    }
  } catch (error) {
    console.error('移除股票失败:', error)
  }
}
```

**src/pages/MarketInsightPage.tsx (第69-85行)**
```typescript
const fetchBasicData = async (forceRefresh: boolean = false) => {
  setLoading(true)
  try {
    const [insightRes, stocksRes] = await Promise.all([
      axios.get('/api/market-insight', { params: { force_refresh: forceRefresh } }),
      axios.get('/api/watchlist', { params: { use_ai: false, force_refresh: forceRefresh } })
    ])
    setMarketInsight(insightRes.data)
    setWatchlist(stocksRes.data) // 问题：直接覆盖，丢失舆情数据
    setMarketLastUpdate(new Date())
    setDataLoaded(true)
  } catch (error) {
    console.error('获取基础数据失败:', error)
  } finally {
    setLoading(false)
  }
}
```

### 同样的问题也存在于添加股票

**src/pages/MarketInsightPage.tsx (第163-175行)**
```typescript
const handleAddStock = async (symbol: string) => {
  try {
    const res = await axios.post(`/api/watchlist/${symbol}`)
    if (res.data.success) {
      // 同样的问题：覆盖所有舆情数据
      await fetchBasicData(false)
      setSearchQuery('')
      setSearchResults([])
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    console.error('添加股票失败:', error)
  }
}
```

## 影响范围

### 直接影响
1. 删除股票后，所有股票的舆情信息消失
2. 添加股票后，所有股票的舆情信息消失
3. 用户需要手动点击"🤖 更新舆情"按钮重新获取

### 用户体验问题
1. **数据丢失感**：用户刚看到的舆情信息突然消失
2. **操作成本高**：每次添加/删除都要重新获取舆情
3. **token浪费**：用户被迫频繁点击"更新舆情"
4. **逻辑不合理**：删除一只股票不应该影响其他股票

## 解决方案

### 方案1：前端状态管理优化（推荐）

**核心思路**：删除/添加股票时，只更新列表结构，保留现有舆情数据

#### 实现步骤

1. **删除股票**：直接从前端状态中移除该股票，不重新获取列表
2. **添加股票**：只获取新股票的数据，合并到现有列表
3. **保留舆情**：不覆盖已有的舆情信息

#### 优点
- 舆情数据不丢失
- 响应速度快（无需重新获取整个列表）
- 用户体验好
- 减少API调用

#### 缺点
- 需要修改前端逻辑

### 方案2：智能合并数据

**核心思路**：获取新数据时，智能合并舆情信息

#### 实现步骤

1. 获取新的基础数据（`use_ai: false`）
2. 遍历新数据，从旧数据中提取舆情信息
3. 合并后更新状态

#### 优点
- 保留舆情数据
- 逻辑清晰

#### 缺点
- 需要额外的合并逻辑
- 仍然需要API调用

### 方案3：后端返回完整数据

**核心思路**：删除/添加股票的API直接返回更新后的完整列表（包含舆情）

#### 优点
- 前端逻辑简单

#### 缺点
- 每次添加/删除都要重新获取舆情（token消耗大）
- 响应慢

## 推荐实施方案

**采用方案1：前端状态管理优化**

### 删除股票优化
```typescript
const handleRemoveStock = async (symbol: string) => {
  if (!confirm(`确定要移除 ${symbol} 吗？`)) return
  try {
    const res = await axios.delete(`/api/watchlist/${symbol}`)
    if (res.data.success) {
      // 直接从前端状态中移除，不重新获取列表
      setWatchlist(prev => prev.filter(stock => stock.symbol !== symbol))
    }
  } catch (error) {
    console.error('移除股票失败:', error)
  }
}
```

### 添加股票优化
```typescript
const handleAddStock = async (symbol: string) => {
  try {
    const res = await axios.post(`/api/watchlist/${symbol}`)
    if (res.data.success) {
      // 只获取新添加股票的数据
      const newStockRes = await axios.get(`/api/stock/${symbol}`)
      // 添加到现有列表
      setWatchlist(prev => [...prev, newStockRes.data])
      setSearchQuery('')
      setSearchResults([])
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    console.error('添加股票失败:', error)
  }
}
```

## 预期效果

### 用户体验
- ✅ 删除股票时，其他股票的舆情信息保留
- ✅ 添加股票时，现有股票的舆情信息保留
- ✅ 操作响应更快（无需重新获取整个列表）
- ✅ 逻辑更合理（局部操作不影响全局）

### 技术指标
- ✅ 减少API调用次数
- ✅ 减少token消耗
- ✅ 提升响应速度
- ✅ 降低服务器负载

## 需要新增的API

### GET /api/stock/{symbol}
获取单只股票的基础数据（不含舆情）

**用途**：添加股票时只获取新股票的数据

**返回示例**：
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "price": 150.25,
  "change": 2.50,
  "changePercent": 1.69,
  "volume": 50000000,
  "volumeHistory": [45000000, 48000000, ...],
  "sentiment": "暂无舆情数据"
}
```
