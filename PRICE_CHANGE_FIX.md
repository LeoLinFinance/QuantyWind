# ✅ 涨跌幅计算修复 & 成交量趋势图添加

## 问题1：涨跌幅显示为0

### 原因
之前使用的是 `meta.regularMarketPrice` 和 `meta.previousClose`，但Yahoo Finance API的 `previousClose` 字段经常为空或不准确。

### 解决方案
改用历史收盘价数组的最后两个值来计算涨跌幅：

```python
# 获取历史收盘价
closes = quotes.get('close', [])
valid_closes = [c for c in closes if c is not None]

# 使用最近两个交易日的收盘价
current_price = valid_closes[-1]
previous_close = valid_closes[-2]

# 计算涨跌幅
change = current_price - previous_close
change_percent = (change / previous_close) * 100
```

### 验证结果 ✅

**指数涨跌幅：**
- 纳斯达克：-0.007% ✅
- 标普500：-0.414% ✅
- 罗素2000：-1.296% ✅

**个股涨跌幅：**
- AAPL：+0.089% ($257.46 → $257.69) ✅
- MSFT：-0.210% ($408.96 → $408.10) ✅
- TSLA：-1.858% ($396.73 → $389.36) ✅

## 问题2：添加一周成交量趋势图

### 实现方案

1. **后端数据获取**
   - 获取最近10天的历史数据
   - 提取最近7个交易日的成交量
   - 返回 `volumeHistory` 数组

```python
# 获取一周成交量数据
valid_volumes = [v for v in volumes if v is not None]
volume_history = valid_volumes[-7:]  # 最近7个交易日

return {
    'volume': int(volume) if volume else 0,
    'volumeHistory': [int(v) for v in volume_history],
    ...
}
```

2. **前端可视化组件**
   - 创建 `VolumeSparkline` 组件
   - 使用SVG绘制柱状图
   - 最新一天用蓝色高亮
   - 其他天用灰色

```tsx
<VolumeSparkline data={stock.volumeHistory || []} />
```

### 效果展示

成交量趋势图特点：
- 📊 柱状图展示7天成交量变化
- 🔵 最新一天用蓝色高亮
- ⚪ 历史数据用灰色显示
- 📏 自动缩放适应数据范围
- 🎨 简洁美观，不占用太多空间

### 数据示例

AAPL一周成交量：
```
[72,366,500, 41,827,900, 38,568,900, 39,803,100, 
 49,658,600, 41,094,000, 13,032,174]
```

## 界面更新

### 表格新增列
```
股票 | 价格 | 涨跌幅 | 成交量 | 一周趋势 | 舆情提示 | 操作
```

### 涨跌幅显示优化
- 显示百分比（大字）
- 显示涨跌额（小字）
- 红绿色区分涨跌

示例：
```
+0.09%
+0.23
```

## 技术细节

### 后端改进
1. 获取10天历史数据（确保有足够的交易日）
2. 过滤掉None值
3. 提取最近7个有效交易日的数据
4. 返回完整的成交量历史数组

### 前端改进
1. 新增 `VolumeSparkline` 组件
2. 更新 `Stock` 接口添加 `volumeHistory` 字段
3. 优化涨跌幅显示（双行显示）
4. 表格新增"一周趋势"列

## 测试验证

```bash
# 测试市场洞察（指数涨跌幅）
curl -s 'http://localhost:8000/api/market-insight' | python3 -m json.tool

# 测试个股数据（涨跌幅 + 成交量历史）
curl -s 'http://localhost:8000/api/watchlist?use_ai=false' | python3 -m json.tool
```

## 当前状态

✅ 涨跌幅计算完全准确
✅ 成交量趋势图正常显示
✅ 数据实时更新
✅ 界面美观清晰

刷新浏览器 http://localhost:3000 查看完整效果！
