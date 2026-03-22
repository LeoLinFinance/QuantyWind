# 投资组合数据加载问题修复

## 问题描述

用户在市场洞察中添加了CSCO、PANW、IONQ、FNKO四个股票，虽然后台日志显示历史数据获取成功（每个股票1254条数据），但在投资组合风险分析中计算时却提示"没有足够的历史数据"。

## 问题原因

**根本原因**：服务实例隔离导致的数据不同步

1. **MarketService** 在添加股票时使用自己的 `HistoricalDataService` 实例获取并保存数据
2. **RiskService** 在计算风险时使用另一个 `HistoricalDataService` 实例读取数据
3. 两个实例在内存中维护各自的数据副本（`self.data`）
4. MarketService保存数据到文件后，RiskService的内存副本没有更新
5. 导致RiskService读取到的是初始化时的空数据

## 技术细节

### 问题代码
```python
# risk_service.py
class RiskService:
    def __init__(self):
        self.historical_service = HistoricalDataService()  # 实例1
        
    def _get_returns_data(self, symbols):
        # 读取的是实例1初始化时加载的数据（空的）
        data = self.historical_service.get_symbol_data(symbol)
```

```python
# market_service.py
class MarketService:
    def __init__(self):
        self.historical_service = HistoricalDataService()  # 实例2
        
    def add_stock(self, symbol):
        # 保存到实例2的内存和文件
        self.historical_service.update_symbol_data(...)
```

### 数据流程
```
添加股票 (MarketService)
    ↓
获取历史数据
    ↓
保存到文件 ✅
保存到实例2内存 ✅
    ↓
计算风险 (RiskService)
    ↓
从实例1内存读取 ❌ (空数据)
    ↓
提示"没有足够的历史数据"
```

## 解决方案

添加 `reload_data()` 公开方法，在计算风险前重新从文件加载最新数据。

### 修改1: historical_data_service.py
```python
def reload_data(self):
    """重新加载数据（公开方法）"""
    self.data = self._load_data()
```

### 修改2: risk_service.py
```python
def _get_returns_data(self, symbols: List[str]) -> Optional[np.ndarray]:
    """获取股票的收益率数据"""
    all_returns = []
    
    # 重新加载数据以确保获取最新的数据
    self.historical_service.reload_data()  # ← 关键修改
    
    for symbol in symbols:
        data = self.historical_service.get_symbol_data(symbol, is_index=False)
        # ... 后续处理
```

## 修复后的数据流程

```
添加股票 (MarketService)
    ↓
获取历史数据
    ↓
保存到文件 ✅
保存到实例2内存 ✅
    ↓
计算风险 (RiskService)
    ↓
调用 reload_data() ← 新增
    ↓
从文件重新加载 ✅
    ↓
从实例1内存读取 ✅ (最新数据)
    ↓
成功计算风险指标
```

## 测试结果

### 修复前
```bash
curl -X POST http://localhost:8000/api/portfolio-risk \
  -d '{"portfolio": [{"symbol": "CSCO", "weight": 0.5}, {"symbol": "PANW", "weight": 0.5}]}'

# 后台日志
⚠️ CSCO 没有足够的历史数据
⚠️ PANW 没有足够的历史数据
```

### 修复后
```bash
curl -X POST http://localhost:8000/api/portfolio-risk \
  -d '{"portfolio": [{"symbol": "CSCO", "weight": 0.5}, {"symbol": "PANW", "weight": 0.5}]}'

# 后台日志
✅ CSCO 加载了 1253 个收益率数据点
✅ PANW 加载了 1253 个收益率数据点
📊 投资组合收益率矩阵: (1253, 2)

# 响应
{
  "success": true,
  "risk_metrics": {
    "var_95": -0.0253,
    "cvar_95": -0.0379,
    "volatility": 0.2629,
    "sharpe_ratio": 0.6329,
    ...
  }
}
```

### 四股票组合测试
```bash
# CSCO + PANW + IONQ + FNKO
✅ CSCO 加载了 1253 个收益率数据点
✅ PANW 加载了 1253 个收益率数据点
✅ IONQ 加载了 1253 个收益率数据点
✅ FNKO 加载了 1253 个收益率数据点
📊 投资组合收益率矩阵: (1253, 4)

风险指标：
- VaR (95%): -3.93%
- CVaR (95%): -5.48%
- 年化波动率: 40.97%
- 夏普比率: 0.62
- 最大回撤: -46.81%
```

## 其他可能的解决方案

### 方案1: 单例模式（未采用）
```python
# 使用单例模式确保只有一个HistoricalDataService实例
class HistoricalDataService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**优点**：彻底解决实例隔离问题
**缺点**：增加复杂度，可能影响测试

### 方案2: 依赖注入（未采用）
```python
# 在初始化时注入共享的HistoricalDataService实例
class RiskService:
    def __init__(self, historical_service: HistoricalDataService):
        self.historical_service = historical_service
```

**优点**：更好的解耦和可测试性
**缺点**：需要修改所有服务的初始化代码

### 方案3: 每次从文件读取（已采用）
```python
# 在需要时重新加载数据
self.historical_service.reload_data()
```

**优点**：简单直接，不改变架构
**缺点**：每次计算都需要读文件（但影响很小）

## 性能影响

- **文件读取时间**：~10ms（JSON文件约2MB）
- **计算时间**：~100ms（1253个数据点，4个股票）
- **总体影响**：可忽略不计

## 经验教训

1. **状态管理**：多个服务实例共享数据时要特别注意同步问题
2. **数据持久化**：内存缓存和文件存储要保持一致
3. **调试技巧**：通过日志追踪数据流向，快速定位问题
4. **测试覆盖**：需要测试跨服务的数据流场景

## 相关文件

- `backend/services/historical_data_service.py` - 添加reload_data方法
- `backend/services/risk_service.py` - 调用reload_data
- `backend/services/market_service.py` - 数据保存逻辑
- `BUG_FIX_PORTFOLIO_DATA.md` - 本文档

## 总结

✅ 问题已修复
✅ 所有新添加的股票都能正常计算风险指标
✅ 数据同步机制正常工作
✅ 性能影响可忽略

现在用户可以：
1. 在市场洞察中添加任意股票
2. 等待8秒自动获取历史数据
3. 在投资组合配置中选择这些股票
4. 成功计算风险指标
