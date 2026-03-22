# 智者论坛 - 完整实现文档

## 项目概述

智者论坛是量数风行平台的第四个核心页面，提供AI驱动的投资决策支持系统。通过KimiClaw资讯机器人和5位专业领域的AI专家，为用户提供全方位的市场分析和投资建议。

## 快速开始

### 1. 安装和启动

```bash
# 1. 初始化测试数据
python init_expert_forum.py

# 2. 启动后端（新终端）
cd backend
python main.py

# 3. 启动前端（新终端）
npm run dev

# 4. 访问页面
# 打开浏览器: http://localhost:5173/expert-forum
```

### 2. 基本使用

1. 打开"接收资讯"开关 → 获取市场动态
2. 打开"开始讨论"开关 → 专家团队分析
3. 点击"配置专家" → 自定义专家提示词

## 架构设计

### 系统架构

```
┌─────────────┐
│   用户界面   │ (React + TypeScript)
└──────┬──────┘
       │
       ↓ HTTP/REST
┌─────────────┐
│  API路由层  │ (FastAPI)
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────┐
│        服务层                    │
│  ┌──────────────────────────┐  │
│  │ ExpertForumService       │  │
│  │  - 协调资讯和专家分析     │  │
│  └────┬─────────────┬────────┘  │
│       │             │            │
│  ┌────▼─────┐  ┌───▼──────────┐│
│  │ KimiClaw │  │ Portfolio    ││
│  │ Service  │  │ Service      ││
│  └──────────┘  └──────────────┘│
└─────────────────────────────────┘
       │
       ↓
┌─────────────┐
│  Kimi API   │ (Moonshot)
└─────────────┘
```

### 数据流

```
1. 资讯流:
   用户开启开关 → 前端定时器 → API请求 → KimiClaw → 返回资讯 → 显示

2. 专家分析流:
   用户开启开关 → 收集上下文 → 依次调用专家 → 每个专家调用Kimi API → 返回分析 → 显示

3. 配置流:
   用户编辑提示词 → 保存到后端 → 写入JSON文件 → 页面加载时读取
```

## 核心组件

### 前端组件

#### ExpertForumPage.tsx
- **状态管理**: 
  - `newsEnabled`: 资讯开关状态
  - `discussionEnabled`: 讨论开关状态
  - `messages`: 对话消息列表
  - `expertConfigs`: 专家配置列表
  - 频率限制时间戳

- **核心功能**:
  - `fetchNews()`: 获取新闻资讯
  - `startExpertDiscussion()`: 启动专家讨论
  - `saveExpertConfig()`: 保存专家配置

- **UI组件**:
  - 控制面板（开关和按钮）
  - 对话区域（消息列表）
  - 配置模态框（编辑提示词）

### 后端服务

#### ExpertForumService
- **职责**: 协调KimiClaw和专家分析
- **方法**:
  - `fetch_news_summary()`: 获取新闻总结
  - `get_expert_analysis()`: 获取专家分析
  - `get_expert_configs()`: 读取配置
  - `save_expert_config()`: 保存配置

#### PortfolioService
- **职责**: 管理投资组合
- **方法**:
  - `get_portfolio()`: 获取持仓
  - `add_holding()`: 添加持仓
  - `remove_holding()`: 移除持仓
  - `get_holdings_symbols()`: 获取股票代码列表

#### KimiResearchService
- **职责**: 调用Kimi API进行在线研究
- **方法**:
  - `_call_kimi_with_search()`: 核心API调用
  - `research_stock()`: 研究单只股票
  - `research_industry()`: 研究行业
  - `research_macro_environment()`: 研究宏观环境

## API接口文档

### 1. 获取新闻资讯

```http
POST /api/expert-forum/news
Content-Type: application/json

{
  "last_time": "2024-01-01T00:00:00"  // 可选，上次获取时间
}

Response:
{
  "content": "【宏观经济】...",
  "timestamp": "2024-01-01T12:00:00",
  "stock_symbols": ["AAPL", "TSLA"]
}
```

### 2. 停止新闻推送

```http
POST /api/expert-forum/news/stop

Response:
{
  "status": "stopped"
}
```

### 3. 获取专家分析

```http
POST /api/expert-forum/expert-analysis
Content-Type: application/json

{
  "expert_id": "stock_analyst",
  "expert_name": "选股分析师",
  "expert_prompt": "你是一位资深选股分析师...",
  "context": "市场最近表现良好..."
}

Response:
{
  "expert_id": "stock_analyst",
  "expert_name": "选股分析师",
  "analysis": "根据当前市场情况...",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 4. 获取专家配置

```http
GET /api/expert-forum/configs

Response:
[
  {
    "id": "stock_analyst",
    "name": "选股分析师",
    "prompt": "你是一位资深选股分析师..."
  }
]
```

### 5. 保存专家配置

```http
POST /api/expert-forum/configs
Content-Type: application/json

{
  "id": "stock_analyst",
  "name": "选股分析师",
  "prompt": "你是一位资深选股分析师..."
}

Response:
{
  "status": "saved"
}
```

## 文件清单

### 新增文件

```
src/pages/ExpertForumPage.tsx              # 智者论坛页面组件
backend/routers/expert_forum.py            # API路由
backend/services/expert_forum_service.py   # 核心服务
backend/services/portfolio_service.py      # 投资组合服务
init_expert_forum.py                       # 初始化脚本
test_expert_forum.py                       # 测试脚本
EXPERT_FORUM_SETUP.md                      # 设置说明
EXPERT_FORUM_QUICKSTART.md                 # 快速启动
EXPERT_FORUM_USER_GUIDE.md                 # 用户指南
KIMICLAW_INTEGRATION.md                    # KimiClaw集成
EXPERT_FORUM_README.md                     # 本文档
```

### 修改文件

```
src/App.tsx                                # 添加路由
src/components/Layout.tsx                  # 添加导航
backend/main.py                            # 添加路由注册
```

### 自动生成文件

```
data/expert_configs.json                   # 专家配置
data/portfolio.json                        # 投资组合
```

## 技术栈

### 前端
- React 18
- TypeScript
- React Router v6
- Tailwind CSS
- 自定义Switch组件（无需额外依赖）

### 后端
- FastAPI
- Python 3.8+
- Kimi API (Moonshot)
- JSON文件存储

## 配置说明

### Kimi API配置

在`backend/services/kimi_research_service.py`中：

```python
self.api_key = "sk-kimi-cpp9rp8QVOmqkmTv51bmaP6rGLRgUUNI1ztpAXjVWfCdi5Mb1nbrdODF5Fd25xJ0"
self.api_url = "https://api.moonshot.cn/v1/chat/completions"
self.model = "moonshot-v1-8k"
```

### 环境变量（可选）

可以将API Key移到`.env`文件：

```env
KIMI_API_KEY=your_api_key_here
```

然后在代码中读取：

```python
import os
self.api_key = os.getenv('KIMI_API_KEY')
```

## 测试

### 运行完整测试

```bash
python test_expert_forum.py
```

测试内容：
1. 投资组合管理
2. 新闻资讯获取
3. 专家配置保存
4. 专家分析功能

### 手动测试

1. 启动服务
2. 访问 http://localhost:5173/expert-forum
3. 测试两个开关功能
4. 测试配置专家功能
5. 检查对话显示是否正常

## 性能优化

### 1. API调用优化
- 使用较小的模型（moonshot-v1-8k）降低成本
- 限制max_tokens减少响应时间
- 添加调用频率限制避免过度使用

### 2. 前端优化
- 消息列表虚拟滚动（大量消息时）
- 防抖处理开关操作
- 缓存专家配置

### 3. 后端优化
- 异步处理API调用
- 添加结果缓存
- 批量处理专家分析

## 扩展功能建议

### 短期（1-2周）
- [ ] 集成实时股票价格API
- [ ] 添加对话历史持久化
- [ ] 支持手动触发单个专家
- [ ] 添加分析结果导出（PDF/Excel）

### 中期（1个月）
- [ ] 支持用户自定义专家
- [ ] 添加专家分析的可视化图表
- [ ] 实现WebSocket实时推送
- [ ] 添加分析结果对比功能

### 长期（3个月）
- [ ] 机器学习优化专家建议
- [ ] 多用户支持和权限管理
- [ ] 移动端适配
- [ ] 集成更多数据源

## 故障排查

### 问题1: 页面无法加载
- 检查前端服务是否启动（npm run dev）
- 检查路由配置是否正确
- 查看浏览器控制台错误

### 问题2: API调用失败
- 检查后端服务是否启动
- 检查Kimi API Key是否有效
- 查看后端日志输出
- 检查网络连接

### 问题3: 配置无法保存
- 检查data目录是否存在
- 检查文件写入权限
- 查看后端日志错误信息

### 问题4: 专家不发言
- 检查调用频率限制
- 查看后端日志是否有错误
- 确认Kimi API额度是否充足

## 维护指南

### 日常维护
- 定期检查API调用量和成本
- 备份专家配置文件
- 监控系统日志

### 更新专家提示词
- 根据市场变化调整分析重点
- 根据用户反馈优化提示词
- 定期测试专家分析质量

### 数据管理
- 定期清理过期数据
- 备份重要配置
- 监控存储空间

## 联系和支持

- 技术文档: 查看本目录下的其他MD文件
- 测试脚本: `test_expert_forum.py`
- 初始化脚本: `init_expert_forum.py`

## 版本历史

### v1.0.0 (2024-01-01)
- ✅ 实现基础对话界面
- ✅ 集成KimiClaw资讯抓取
- ✅ 实现5位专家Agent
- ✅ 支持专家提示词配置
- ✅ 添加调用频率限制
- ✅ 实现配置持久化

### 计划中的功能
- 对话历史持久化
- 实时股票价格集成
- 分析结果可视化
- 用户自定义专家
