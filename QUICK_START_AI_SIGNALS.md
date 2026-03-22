# AI信号功能 - 快速开始

## 🚀 立即使用

AI信号功能已修复并可以正常使用！

### 前提条件

1. ✅ AI模型已配置：`step-1v-8k`（经济型8k模型）
2. ✅ API Key已设置
3. ⚠️ 需要历史数据：请先在前端添加股票到盯盘列表

### 使用步骤

#### 1. 添加股票到盯盘
```
前端 → 市场洞察 → 搜索股票（如AAPL）→ 添加
等待几分钟让系统获取历史数据
```

#### 2. 使用AI分析
```
前端 → 市场洞察 → 个股盯盘表格 → 点击"🤖 分析"按钮
```

#### 3. 查看交易信号
```
前端 → 市场洞察 → 个股盯盘表格 → 点击"📊 信号"按钮
```

## 🧪 测试功能

### 运行测试脚本
```bash
python3 test_ai_signals.py
```

### 预期输出
```
✅ 服务初始化成功
✅ AI API调用成功
✅ 自定义提示词功能正常
🎉 AI信号功能测试完成！
```

## 🎨 自定义提示词

### 查看当前提示词
```bash
curl http://localhost:8000/api/ai-signals/prompts
```

### 设置个股分析提示词
```bash
curl -X POST http://localhost:8000/api/ai-signals/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_type": "stock_analysis",
    "prompt": "你是一个专注于技术分析的分析师。请基于技术指标给出简洁的分析。今天是{current_date}。"
  }'
```

### 设置交易信号提示词
```bash
curl -X POST http://localhost:8000/api/ai-signals/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_type": "trading_signal",
    "prompt": "你是一个短线交易专家。请给出明确的买卖信号。今天是{current_date}。"
  }'
```

### 恢复默认提示词
```bash
# 恢复个股分析默认提示词
curl -X DELETE http://localhost:8000/api/ai-signals/prompts/stock_analysis

# 恢复交易信号默认提示词
curl -X DELETE http://localhost:8000/api/ai-signals/prompts/trading_signal
```

## 🔍 故障排查

### 问题：点击按钮没有反应
**检查**：
1. 打开浏览器开发者工具（F12）
2. 查看Console是否有错误
3. 查看Network标签，检查API请求状态

### 问题：提示"历史数据不足"
**解决**：
1. 确认股票已添加到盯盘列表
2. 等待3-5分钟让系统获取数据
3. 刷新页面后重试

### 问题：AI分析返回"暂时不可用"
**检查**：
1. 后端日志是否有错误信息
2. API Key是否正确
3. 网络连接是否正常

**查看后端日志**：
```bash
# 如果使用uvicorn运行
# 日志会直接显示在终端
```

## 📊 API端点

### AI分析相关
```
GET  /api/ai-signals/analyze/{symbol}        # 个股分析
GET  /api/ai-signals/trading-signal/{symbol} # 交易信号
POST /api/ai-signals/optimize-portfolio      # 组合优化
POST /api/ai-signals/market-trend            # 市场趋势
POST /api/ai-signals/risk-monitor            # 风险监控
```

### 提示词管理
```
GET    /api/ai-signals/prompts                # 获取所有提示词
GET    /api/ai-signals/prompts/{type}         # 获取指定提示词
POST   /api/ai-signals/prompts                # 设置提示词
DELETE /api/ai-signals/prompts/{type}         # 删除提示词
```

## 💡 使用技巧

### 1. 提示词优化
- 明确指定输出格式（JSON）
- 限制输出长度（避免超出token限制）
- 包含日期变量 `{current_date}`

### 2. 缓存利用
- 相同股票的分析会缓存1小时
- 避免频繁点击同一股票
- 如需强制刷新，等待1小时后重试

### 3. 批量分析
- 可以依次分析多只股票
- 建议间隔几秒钟避免API限流

## 📚 更多信息

- 详细修复说明：`AI_SIGNALS_FIX_SUMMARY.md`
- 功能实现文档：`AI_SIGNALS_IMPLEMENTATION.md`
- 测试脚本：`test_ai_signals.py`

---

**提示**：AI分析功能已修复，现在可以正常使用了！
