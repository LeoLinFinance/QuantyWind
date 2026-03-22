# 自动刷新功能 - 实现完成

## 完成时间
2026年3月10日

## 功能概述

在导航栏最右侧添加了iOS风格的自动刷新开关，用户可以手动开启/关闭自动刷新功能。开启后，系统会每15分钟自动刷新当前页面的数据。

## 功能特性

### 1. iOS风格开关
- 位置：导航栏最右侧（三个页面切换tab的右边）
- 样式：仿iOS系统的滑动开关
- 颜色：关闭时灰色，开启时蓝色
- 动画：平滑的滑动过渡效果

### 2. 自动刷新机制
- 刷新间隔：15分钟（900秒）
- 刷新范围：只刷新当前激活的页面
- 智能识别：自动识别用户当前所在页面
- 独立刷新：不同页面的刷新互不影响

### 3. 状态指示
- 开关状态：清晰显示开/关状态
- 运行指示：开启时显示绿色"● 运行中"动画
- 文字说明："自动刷新 (15分钟)"

## 技术实现

### 1. DataContext扩展

**文件**: `src/contexts/DataContext.tsx`

**新增状态**:
```typescript
interface DataContextType {
  // ... 原有状态
  
  // 自动刷新功能
  autoRefreshEnabled: boolean
  setAutoRefreshEnabled: (enabled: boolean) => void
  refreshCurrentPage: () => void
  setRefreshCurrentPage: (fn: () => void) => void
}
```

**功能说明**:
- `autoRefreshEnabled`: 自动刷新开关状态（全局）
- `setAutoRefreshEnabled`: 切换开关状态
- `refreshCurrentPage`: 当前页面的刷新函数
- `setRefreshCurrentPage`: 注册当前页面的刷新函数

### 2. Layout组件更新

**文件**: `src/components/Layout.tsx`

**核心逻辑**:
```typescript
// 自动刷新定时器
useEffect(() => {
  if (!autoRefreshEnabled) return

  const interval = setInterval(() => {
    console.log('🔄 自动刷新触发 - 15分钟定时更新')
    refreshCurrentPage()
  }, 15 * 60 * 1000) // 15分钟

  return () => clearInterval(interval)
}, [autoRefreshEnabled, refreshCurrentPage])
```

**UI组件**:
```tsx
<div className="flex items-center space-x-3">
  <span className="text-sm text-gray-600">自动刷新 (15分钟)</span>
  <button
    onClick={toggleAutoRefresh}
    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
      autoRefreshEnabled ? 'bg-blue-600' : 'bg-gray-300'
    }`}
  >
    <span
      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
        autoRefreshEnabled ? 'translate-x-6' : 'translate-x-1'
      }`}
    />
  </button>
  {autoRefreshEnabled && (
    <span className="text-xs text-green-600 animate-pulse">● 运行中</span>
  )}
</div>
```

### 3. 页面刷新函数注册

**三个页面都需要注册刷新函数**:

#### MarketInsightPage
```typescript
useEffect(() => {
  // 注册当前页面的刷新函数到Context
  setRefreshCurrentPage(() => fetchData)
  
  // ... 其他初始化逻辑
}, [])
```

#### RiskAnalysisPage
```typescript
useEffect(() => {
  // 注册当前页面的刷新函数到Context
  setRefreshCurrentPage(() => fetchData)
  
  // ... 其他初始化逻辑
}, [])
```

#### SentimentMapPage
```typescript
useEffect(() => {
  // 注册当前页面的刷新函数到Context
  setRefreshCurrentPage(() => fetchData)
  
  // ... 其他初始化逻辑
}, [])
```

## 工作流程

### 1. 用户开启自动刷新

```
用户操作：
1. 点击导航栏右侧的开关
2. 开关从灰色变为蓝色
3. 显示"● 运行中"绿色指示

系统行为：
1. setAutoRefreshEnabled(true)
2. 启动15分钟定时器
3. 记录当前页面的刷新函数
```

### 2. 自动刷新触发

```
时间到达（15分钟后）：
1. 定时器触发
2. 调用 refreshCurrentPage()
3. 执行当前页面的 fetchData()
4. 更新页面数据
5. 控制台输出: "🔄 自动刷新触发 - 15分钟定时更新"
```

### 3. 页面切换

```
用户切换页面：
1. 从"市场洞察"切换到"风险分析"
2. 新页面的 useEffect 执行
3. setRefreshCurrentPage(() => fetchData) 更新刷新函数
4. 下次定时器触发时，会刷新"风险分析"页面
```

### 4. 用户关闭自动刷新

```
用户操作：
1. 点击导航栏右侧的开关
2. 开关从蓝色变为灰色
3. "● 运行中"指示消失

系统行为：
1. setAutoRefreshEnabled(false)
2. 清除定时器 clearInterval(interval)
3. 停止自动刷新
```

## 使用场景

### 场景1：盯盘模式
```
用户需求：
- 长时间监控市场数据
- 不想手动点击刷新按钮

操作：
1. 打开"市场洞察盯盘"页面
2. 开启自动刷新开关
3. 每15分钟自动更新股票价格、涨跌幅、AI舆情分析
```

### 场景2：风险监控
```
用户需求：
- 持续监控风险指标变化
- 及时发现风险信号

操作：
1. 打开"风险分析看板"页面
2. 开启自动刷新开关
3. 每15分钟自动更新风险模型数据
```

### 场景3：舆情追踪
```
用户需求：
- 实时关注市场舆情变化
- 追踪风险事件发展

操作：
1. 打开"市场风险舆情地图"页面
2. 开启自动刷新开关
3. 每15分钟自动更新舆情事件和产业链洞察
```

## 性能优化

### 1. 智能刷新
- 只刷新当前激活的页面
- 不刷新后台页面
- 避免不必要的API调用

### 2. 定时器管理
```typescript
useEffect(() => {
  if (!autoRefreshEnabled) return

  const interval = setInterval(() => {
    refreshCurrentPage()
  }, 15 * 60 * 1000)

  return () => clearInterval(interval) // 组件卸载时清除定时器
}, [autoRefreshEnabled, refreshCurrentPage])
```

### 3. 状态持久化
- 开关状态保存在Context中
- 页面切换时状态不丢失
- 刷新函数动态更新

## Token消耗估算

### 开启自动刷新后的消耗

**市场洞察页面**:
- 每次刷新: ~500 tokens（含AI分析）
- 每小时: ~2000 tokens（4次刷新）
- 每天: ~48000 tokens（假设8小时盯盘）

**风险分析页面**:
- 每次刷新: ~200 tokens
- 每小时: ~800 tokens
- 每天: ~19200 tokens

**舆情地图页面**:
- 每次刷新: ~3000 tokens（15条新闻+产业链洞察）
- 每小时: ~12000 tokens
- 每天: ~288000 tokens

**建议**:
- 根据实际需求选择性开启
- 不需要时及时关闭
- 可以考虑调整刷新间隔（如30分钟）

## 用户体验

### 优点
✅ 无需手动刷新，自动保持数据最新
✅ iOS风格开关，操作直观
✅ 清晰的状态指示
✅ 只刷新当前页面，节省资源
✅ 可随时开启/关闭

### 注意事项
⚠️ 开启后会增加token消耗
⚠️ 建议在需要时才开启
⚠️ 长时间不使用时建议关闭
⚠️ 15分钟间隔适合大多数场景

## 未来扩展

### 短期（1周内）
1. **可配置刷新间隔**
   - 添加下拉菜单选择间隔（5分钟、15分钟、30分钟、1小时）
   - 保存用户偏好设置

2. **刷新历史记录**
   - 显示最近一次自动刷新时间
   - 显示今日自动刷新次数

### 中期（1个月内）
1. **智能刷新**
   - 根据市场开盘/收盘时间调整刷新频率
   - 盘中更频繁，盘后降低频率

2. **刷新通知**
   - 刷新完成后显示toast提示
   - 数据有重大变化时高亮显示

3. **暂停/恢复**
   - 添加暂停按钮（不关闭开关，只是暂停定时器）
   - 用户可以临时暂停自动刷新

### 长期（3个月内）
1. **条件刷新**
   - 只在数据变化超过阈值时刷新
   - 减少不必要的API调用

2. **后台刷新**
   - 使用Web Worker在后台刷新数据
   - 不阻塞UI线程

3. **离线缓存**
   - 刷新失败时使用缓存数据
   - 网络恢复后自动重试

## 测试验证

### 功能测试
✅ 开关切换正常
✅ 定时器启动/停止正常
✅ 页面刷新正常
✅ 页面切换时刷新函数更新正常
✅ 状态指示显示正常

### 性能测试
✅ 定时器不会泄漏
✅ 页面切换不会重复注册
✅ 只刷新当前页面
✅ 内存占用正常

### 用户体验测试
✅ 开关操作流畅
✅ 状态指示清晰
✅ 刷新不影响用户操作
✅ 控制台日志清晰

## 代码变更总结

### 修改的文件
1. `src/contexts/DataContext.tsx` - 添加自动刷新状态管理
2. `src/components/Layout.tsx` - 添加iOS风格开关和定时器
3. `src/pages/MarketInsightPage.tsx` - 注册刷新函数
4. `src/pages/RiskAnalysisPage.tsx` - 注册刷新函数
5. `src/pages/SentimentMapPage.tsx` - 注册刷新函数

### 新增功能
- 自动刷新开关（iOS风格）
- 15分钟定时刷新机制
- 当前页面刷新函数注册
- 运行状态指示

### 代码行数
- 新增代码：约100行
- 修改代码：约20行
- 总计：约120行

## 总结

成功实现了自动刷新功能，用户可以通过导航栏右侧的iOS风格开关来控制是否每15分钟自动刷新当前页面的数据。

**主要成就**:
✅ iOS风格的开关UI
✅ 智能的页面刷新机制
✅ 清晰的状态指示
✅ 良好的性能表现
✅ 优秀的用户体验

**用户价值**:
- 无需手动刷新，自动保持数据最新
- 灵活控制，可随时开启/关闭
- 节省资源，只刷新当前页面
- 操作简单，一键开启

---

**实现完成时间**: 2026年3月10日
**实现状态**: ✅ 完成
**测试状态**: ✅ 通过
**上线状态**: ✅ 可以部署
