# AI分析功能快速修复指南

## 问题
市场洞察页面的"🤖 分析"和"📊 信号"按钮无法使用

## 快速修复（3步）

### 步骤1: 初始化数据
```bash
python3 init_mock_data.py
```

预期输出：
```
✅ 模拟历史数据初始化完成!
数据文件: data/historical/market_data.json
文件大小: 0.85 MB
股票数量: 10
```

### 步骤2: 启动后端
```bash
cd backend
python3 main.py
```

预期输出：
```
✅ AI服务初始化: 使用阶跃星辰模型 step-1v-8k
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 步骤3: 启动前端
```bash
# 新终端
npm run dev
```

预期输出：
```
➜  Local:   http://localhost:3000/
```

## 验证

1. 访问 http://localhost:3000
2. 进入"市场洞察盯盘"页面
3. 点击任意股票的"🤖 分析"按钮
4. 应该看到AI分析结果弹窗

## 如果还有问题

运行诊断：
```bash
python3 diagnose_ai_signals.py
```

查看详细错误：
```bash
python3 test_ai_signals_detailed.py
```

## 完整文档

- 详细归因: `AI_SIGNALS_DEBUG_REPORT.md`
- 完整方案: `AI_SIGNALS_FIX_COMPLETE.md`
- 修复总结: `AI_SIGNALS_FIXED_SUMMARY.md`
