# 多数据源策略 - 获取完整历史数据

## 策略概述

使用多个免费数据源组合，获取完整的历史数据：

1. **Alpaca Markets** - 主数据源（7年+历史）
2. **Twelve Data** - 备用数据源
3. **Alpha Vantage** - 实时数据（已配置）

## 数据源详细对比

### 1. Alpaca Markets ⭐ 推荐

**优势**:
- ✅ 7年+历史数据
- ✅ 10,000次/分钟（超高频率！）
- ✅ 完全免费
- ✅ 开发者友好

**限制**:
- 需要注册账号
- 主要支持美股

**注册**: https://alpaca.markets/

### 2. Twelve Data

**优势**:
- ✅ 完整历史数据
- ✅ 支持全球市场
- ✅ 多种输出格式

**限制**:
- 8次/分钟（较慢）
- 1,000次/天

**注册**: https://twelvedata.com/

### 3. IEX Cloud

**优势**:
- ✅ 5年+历史数据
- ✅ 50,000次/月
- ✅ 交易所级数据

**限制**:
- 需要注册
- 主要支持美股

**注册**: https://iexcloud.io/

### 4. Alpha Vantage（已配置）

**优势**:
- ✅ 已配置可用
- ✅ 实时数据

**限制**:
- 免费版只有100天

## 实施策略

### 阶段1: 集成Alpaca（立即）⭐

**目标**: 获取7年历史数据

**步骤**:
1. 注册Alpaca账号
2. 获取API key
3. 实现Alpaca数据获取
4. 更新历史数据

**预期结果**:
- 每个标的约1,750天数据（7年）
- 12个标的 = 21,000条数据
- 耗时: 约2分钟（高频率）

### 阶段2: 保留Alpha Vantage作为实时数据源

**用途**:
- 每日增量更新
- 实时价格数据
- 备用数据源

### 阶段3: 添加Twelve Data作为补充（可选）

**用途**:
- 补充缺失数据
- 全球市场数据
- 多时间周期数据

## Alpaca集成实现

### 1. 注册Alpaca账号

访问: https://alpaca.markets/
- 选择"Paper Trading"（模拟交易，免费）
- 填写注册信息
- 获取API Key和Secret

### 2. 配置API Key

在.env文件中添加：
```env
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
```

### 3. 数据获取策略

**多源优先级**:
```
1. 尝试Alpaca（7年数据）
   ↓ 如果失败
2. 尝试Alpha Vantage（100天数据）
   ↓ 如果失败
3. 返回空数据
```

**增量更新**:
```
1. 检查现有数据的最后日期
2. 只获取缺失的日期
3. 合并到现有数据
```

## 数据合并策略

### 场景1: 首次获取

```
Alpaca: 2019-03-10 到 2026-03-10 (7年)
↓
保存到数据库
```

### 场景2: 增量更新

```
现有数据: 2019-03-10 到 2026-03-09
Alpha Vantage: 2026-03-10 (今天)
↓
合并: 2019-03-10 到 2026-03-10
```

### 场景3: 数据补全

```
现有数据: 2025-03-10 到 2026-03-10 (1年)
Alpaca: 2019-03-10 到 2026-03-10 (7年)
↓
合并: 2019-03-10 到 2026-03-10 (完整7年)
```

## 实现代码结构

```python
class HistoricalDataService:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.alpaca_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    
    def _fetch_history(self, symbol, start_date, end_date):
        # 优先使用Alpaca
        if self.alpaca_key:
            data = self._fetch_from_alpaca(symbol, start_date, end_date)
            if data:
                return data
        
        # 备用Alpha Vantage
        if self.alpha_vantage_key:
            data = self._fetch_from_alpha_vantage(symbol, start_date, end_date)
            if data:
                return data
        
        return []
    
    def _fetch_from_alpaca(self, symbol, start_date, end_date):
        # Alpaca API实现
        pass
    
    def _fetch_from_alpha_vantage(self, symbol, start_date, end_date):
        # 现有实现
        pass
```

## 优势

### 1. 数据完整性

- ✅ 7年历史数据（Alpaca）
- ✅ 实时更新（Alpha Vantage）
- ✅ 数据冗余（多源备份）

### 2. 高可用性

- ✅ 主数据源失败时自动切换
- ✅ 多个免费额度
- ✅ 降低单点故障风险

### 3. 成本效益

- ✅ 完全免费
- ✅ 高频率限制
- ✅ 足够的每日配额

## 下一步

### 立即行动

1. **注册Alpaca账号**
   - 访问: https://alpaca.markets/
   - 选择Paper Trading
   - 获取API Key

2. **提供API Key**
   - 告诉我你的Alpaca API Key和Secret
   - 我会立即实现集成

3. **测试数据获取**
   - 获取7年历史数据
   - 验证数据质量

### 预期结果

**数据集统计**:
- 市场指数: 3个 × 1,750天 = 5,250条
- 活跃股票: 9个 × 1,750天 = 15,750条
- 总计: 21,000条数据
- 时间范围: 2019-03-10 到 2026-03-10

**更新时间**:
- 首次更新: 约2分钟（Alpaca高频率）
- 日常更新: <30秒（Alpha Vantage）

## 总结

使用多数据源策略可以：

✅ 获取7年完整历史数据
✅ 保持实时更新能力
✅ 提高系统可靠性
✅ 完全免费

现在请注册Alpaca账号并提供API Key，我会立即实现集成！

---

**策略制定时间**: 2026年3月10日
**推荐数据源**: Alpaca Markets
**预期数据量**: 21,000条（7年）
**状态**: ⏳ 等待Alpaca API Key
