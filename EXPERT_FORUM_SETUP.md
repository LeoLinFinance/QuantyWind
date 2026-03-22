# 智者论坛功能实现说明

## 功能概述

"智者论坛"是量数风行平台的第四个页面，提供类似ChatBot对话的界面，集成了KimiClaw资讯抓取和5个专家agent的智能分析功能。

## 核心功能

### 1. 接收资讯开关
- 控制KimiClaw自动抓取市场新闻
- 打开时立即获取一次资讯，之后每小时自动更新
- 关闭时停止推送并通知KimiClaw

### 2. 开始讨论开关
- 控制5个专家agent的讨论
- 包含调用频率限制（每10分钟一次，选股分析师每天一次）
- 专家按顺序依次发言

### 3. 五位专家Agent
1. **选股分析师**（投前分析）- 每天调用一次
2. **产业链分析师**（投中分析）
3. **市场分析师**（短期价格投资分析）
4. **长期价值投资分析师**（投后管理）
5. **首席经济学家**（投资总监）

### 4. 专家配置功能
- 可编辑每个专家的提示词
- 配置自动保存到`data/expert_configs.json`
- 不会因页面刷新而丢失

## 安装步骤

### 1. 安装前端依赖

```bash
npm install @headlessui/react
```

### 2. 创建数据目录

```bash
mkdir -p data
```

### 3. 启动后端服务

```bash
cd backend
python main.py
```

### 4. 启动前端服务

```bash
npm run dev
```

## 文件结构

### 前端文件
- `src/pages/ExpertForumPage.tsx` - 智者论坛主页面
- `src/App.tsx` - 添加了新路由
- `src/components/Layout.tsx` - 添加了导航链接

### 后端文件
- `backend/routers/expert_forum.py` - API路由
- `backend/services/expert_forum_service.py` - 核心业务逻辑
- `backend/services/portfolio_service.py` - 投资组合管理
- `backend/services/kimi_research_service.py` - Kimi API集成（已存在）
- `backend/main.py` - 添加了新路由

### 数据文件
- `data/expert_configs.json` - 专家配置存储
- `data/portfolio.json` - 投资组合数据

## API接口说明

### 1. 获取新闻资讯
```
POST /api/expert-forum/news
Body: { "last_time": "2024-01-01T00:00:00" }
```

### 2. 停止新闻推送
```
POST /api/expert-forum/news/stop
```

### 3. 获取专家分析
```
POST /api/expert-forum/expert-analysis
Body: {
  "expert_id": "stock_analyst",
  "expert_name": "选股分析师",
  "expert_prompt": "...",
  "context": "..."
}
```

### 4. 获取专家配置
```
GET /api/expert-forum/configs
```

### 5. 保存专家配置
```
POST /api/expert-forum/configs
Body: {
  "id": "stock_analyst",
  "name": "选股分析师",
  "prompt": "..."
}
```

## KimiClaw集成说明

### API配置
KimiClaw使用Kimi API（Moonshot）进行在线研究：
- API Key: 已在`kimi_research_service.py`中配置
- 模型: moonshot-v1-8k
- 功能: 启用web_search进行实时信息搜索

### 输入格式
当"接收资讯"开关打开时，系统会发送以下格式的查询：

```
请帮我总结{最后一次发送资讯的时间}到目前关键的金融经济资讯：

1. 宏观经济信息（GDP、通胀、就业等关键指标）
2. 全球金融市场动态（美股、港股、债券、外汇等）
3. 市场及国家风险舆情
4. 各国央行和美联储的态度与政策
5. 目前持有的股票情况：AAPL, TSLA, NVDA...
```

### 输出格式
KimiClaw返回的资讯会以消息形式显示在对话区域，包含：
- 角色标识：KimiClaw资讯
- 时间戳
- 资讯内容

## 专家Agent工作流程

### 调用顺序
1. 用户打开"开始讨论"开关
2. 系统检查调用频率限制
3. 收集上下文（所有历史消息）
4. 获取当前持仓和股票价格
5. 依次调用5个专家（选股分析师可能跳过）
6. 每个专家分析后延迟2秒（避免API限流）
7. 完成后显示"专家讨论完成"

### 上下文传递
每个专家都会收到：
- 专家自己的提示词
- 完整的对话历史
- 当前持仓信息
- 股票当前价格

### 频率限制
- 普通专家：每10分钟可调用一次
- 选股分析师：每24小时只调用一次

## 使用说明

### 1. 开启资讯接收
1. 打开"接收资讯"开关
2. 系统立即获取最新资讯
3. 之后每小时自动更新
4. 关闭开关停止推送

### 2. 配置专家
1. 点击"配置专家"按钮
2. 选择要编辑的专家
3. 点击"编辑"修改提示词
4. 点击"保存"保存配置

### 3. 开启专家讨论
1. 确保有足够的上下文信息
2. 打开"开始讨论"开关
3. 等待专家依次发言
4. 查看分析结果

## 注意事项

1. **API限流**：Kimi API有调用限制，请合理使用
2. **数据持久化**：专家配置会自动保存，但对话历史不会持久化
3. **股票价格**：需要确保股票价格数据准确（待集成实时价格API）
4. **错误处理**：如果API调用失败，会在控制台显示错误信息

## 后续优化建议

1. 添加对话历史持久化
2. 集成实时股票价格API
3. 添加专家分析结果的可视化展示
4. 支持用户自定义专家
5. 添加分析结果导出功能
6. 优化API调用频率和成本

## 故障排查

### 前端问题
- 检查浏览器控制台错误
- 确认API地址正确（http://localhost:8000）
- 检查网络请求状态

### 后端问题
- 检查Python日志输出
- 确认Kimi API Key有效
- 检查数据目录权限

### 数据问题
- 检查`data/expert_configs.json`格式
- 检查`data/portfolio.json`是否存在
- 确认文件读写权限
