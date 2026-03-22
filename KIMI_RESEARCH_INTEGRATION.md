# Kimi Code在线研究集成文档

## 概述

已成功集成Kimi Code的web_search功能到AI分析服务，实现实时在线信息获取，大幅提升分析的准确性和时效性。

## 核心功能

### 1. 在线股票研究
使用Kimi Code的web_search功能，实时获取：
- 最新财务数据
- 近期重大新闻
- 分析师评级和目标价
- 行业地位和竞争优势
- 主要风险因素

### 2. 数据源整合
AI分析现在整合了多个数据源：
- ✅ 历史价格数据（来自历史数据服务）
- ✅ 技术指标（MA、MACD、RSI、布林带）
- ✅ 风险指标（波动率、最大回撤、夏普比率）
- ✅ 舆情信息（新闻和情感分析）
- ✅ 在线研究（Kimi Code实时搜索）

## 技术实现

### 新增文件

#### 1. `backend/services/kimi_research_service.py`
Kimi Code研究服务，提供：
- `research_stock()`: 股票深度研究
- `research_industry()`: 行业趋势研究
- `research_macro_environment()`: 宏观经济研究
- `quick_research()`: 快速研究特定方面

#### 2. `.kiro/skills/kimi-code-research.md`
Kimi Code技能文档，包含：
- API配置信息
- 使用场景说明
- 调用示例代码
- 研究模板
- 最佳实践

#### 3. `sync_historical_data.py`
数据同步脚本，用于：
- 检查历史数据状态
- 验证数据质量
- 提供数据管理建议

### 修改文件

#### `backend/services/ai_signals_service.py`
- 导入KimiResearchService
- 在`__init__`中初始化Kimi研究服务
- 在`analyze_stock`方法中集成在线研究
- 将研究结果添加到AI分析prompt中

## API配置

### Kimi Code API
```python
API_ID = "19cdc354-b242-8ea9-8000-000006667892"
API_KEY = "sk-kimi-cpp9rp8QVOmqkmTv51bmaP6rGLRgUUNI1ztpAXjVWfCdi5Mb1nbrdODF5Fd25xJ0"
ENDPOINT = "https://api.moonshot.cn/v1/chat/completions"
MODEL = "moonshot-v1-32k"
```

### 启用Web Search
```python
'tools': [
    {
        'type': 'builtin_function',
        'function': {
            'name': '$web_search'
        }
    }
]
```

## 使用流程

### 1. 数据准备
```bash
# 检查数据状态
python3 sync_historical_data.py

# 如果需要，初始化数据
python3 init_mock_data.py
```

### 2. 启动服务
```bash
# 后端
cd backend
python3 main.py

# 前端
npm run dev
```

### 3. 使用AI分析
1. 访问市场洞察页面
2. 点击"🤖 分析"按钮
3. 系统会自动：
   - 加载历史数据
   - 计算技术指标
   - 获取风险指标
   - 分析舆情信息
   - **调用Kimi Code进行在线研究**
   - 综合所有信息生成分析报告

## 分析流程

```
用户点击"分析"
    ↓
加载历史数据 (365天)
    ↓
计算技术指标 (MA, MACD, RSI, BB)
    ↓
计算风险指标 (波动率, 回撤, 夏普)
    ↓
获取舆情信息 (新闻 + 情感)
    ↓
🔍 Kimi Code在线研究 (NEW!)
    ├─ 最新财务数据
    ├─ 重大新闻事件
    ├─ 分析师评级
    ├─ 竞争优势
    └─ 风险因素
    ↓
整合所有信息
    ↓
AI生成分析报告
    ├─ 宏观环境分析
    ├─ 行业趋势分析
    ├─ 公司基本面分析
    ├─ 技术面分析
    └─ 综合评分
    ↓
展示给用户
```

## 优势对比

### 集成前
- ❌ 只有历史数据和技术指标
- ❌ 信息滞后，缺乏实时性
- ❌ 无法获取最新财务数据
- ❌ 缺少分析师观点
- ❌ 风险因素识别不全

### 集成后
- ✅ 多维度数据整合
- ✅ 实时在线信息
- ✅ 最新财务和新闻
- ✅ 分析师评级和目标价
- ✅ 全面的风险识别
- ✅ 更准确的投资建议

## 示例输出

### 在线研究信息示例
```
【在线研究信息】（来自Kimi Code实时搜索）

1. 财务表现：
   Q4营收同比增长15%，净利润增长20%，超出市场预期。
   毛利率提升至45%，显示定价能力增强。

2. 重大新闻：
   - 宣布新产品线，预计明年贡献10%营收
   - 与主要客户签订长期合作协议
   - CEO在财报会议上表示对未来增长充满信心

3. 分析师评级：
   平均目标价$180，较当前价格有12%上涨空间。
   15家机构中，10家给予"买入"评级。

4. 竞争优势：
   技术领先，品牌认知度高，客户粘性强。
   供应链管理优秀，成本控制能力突出。

5. 风险因素：
   宏观经济放缓可能影响需求。
   竞争加剧可能压缩利润率。
   汇率波动带来不确定性。
```

## 性能优化

### 缓存策略
- 在线研究结果缓存1小时
- 避免重复调用API
- 降低成本和延迟

### 错误处理
- 在线研究失败时降级到基础分析
- 不影响核心功能
- 记录详细日志便于排查

### 超时控制
- API调用超时设置为60秒
- 避免长时间等待
- 提供友好的错误提示

## 成本控制

### API配额管理
- Kimi Code有调用限制
- 使用缓存减少调用次数
- 只在必要时启用在线研究

### 建议
1. 生产环境监控API使用量
2. 设置每日调用上限
3. 实现配额预警机制
4. 考虑批量研究优化

## 数据同步

### 历史数据来源
AI分析服务使用的历史数据与风险分析页面共享：
- 数据文件：`data/historical/market_data.json`
- 数据服务：`HistoricalDataService`
- 自动重载：风险服务会自动重载最新数据

### 数据更新
```bash
# 方法1：使用同步脚本检查
python3 sync_historical_data.py

# 方法2：通过API更新
curl -X POST http://localhost:8000/api/historical-data/update

# 方法3：重新初始化
python3 init_mock_data.py
```

## 测试验证

### 1. 测试Kimi研究服务
```python
from backend.services.kimi_research_service import KimiResearchService

service = KimiResearchService()
result = service.research_stock('AAPL')
print(result['research_content'])
```

### 2. 测试完整AI分析
```bash
python3 test_ai_signals_detailed.py
```

预期看到：
```
🔍 使用Kimi Code研究 AAPL...
✅ 在线研究完成: 1234 字符
🤖 调用阶跃星辰API: 模型=step-1v-32k, max_tokens=1000
✅ AI响应成功: 620 字符
✅ 分析成功!
```

### 3. 浏览器测试
1. 打开市场洞察页面
2. 点击"🤖 分析"
3. 查看浏览器控制台日志
4. 验证分析结果包含在线研究信息

## 故障排查

### 问题1：在线研究失败
**症状**：日志显示"在线研究失败"

**解决方案**：
1. 检查API密钥是否正确
2. 检查网络连接
3. 查看详细错误日志
4. 系统会自动降级到基础分析

### 问题2：数据不足
**症状**：提示"历史数据不足"

**解决方案**：
```bash
# 检查数据状态
python3 sync_historical_data.py

# 初始化数据
python3 init_mock_data.py
```

### 问题3：分析超时
**症状**：等待时间过长

**原因**：在线研究需要时间

**优化**：
- 已设置60秒超时
- 使用缓存避免重复调用
- 考虑异步处理

## 未来优化

### 1. 异步处理
- 在线研究异步执行
- 先返回基础分析
- 研究完成后更新

### 2. 批量研究
- 一次调用研究多只股票
- 降低API调用次数
- 提高效率

### 3. 智能缓存
- 根据市场开盘时间调整缓存
- 重要事件发生时清除缓存
- 个性化缓存策略

### 4. 研究深度控制
- 快速模式：只获取关键信息
- 深度模式：全面研究
- 用户可选择

## 总结

通过集成Kimi Code的web_search功能，AI分析服务现在能够：
- ✅ 获取实时市场信息
- ✅ 整合多维度数据
- ✅ 提供更准确的分析
- ✅ 识别最新风险和机会
- ✅ 给出更有价值的投资建议

这大大提升了系统的实用价值和竞争力！
