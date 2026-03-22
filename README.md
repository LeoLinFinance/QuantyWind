# 量数风行 QuantyWind

> 个人美股舆情风险专家 - 基于 AI 的智能投资分析平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

## 📖 项目简介

量数风行是一个开源的美股投资分析平台，集成了多个 AI 大模型，为个人投资者提供：

- 🤖 **智者论坛**：多专家 AI 对话，获取不同角度的投资建议
- 📊 **市场洞察**：实时市场数据和 AI 分析
- ⚠️ **风险分析**：投资组合风险评估和解读
- 🗺️ **舆情地图**：市场情绪可视化分析
- 📈 **智能信号**：AI 驱动的交易信号和个股分析

## ✨ 核心特性

### 1. 多专家 AI 对话系统
- 支持多个专业领域的 AI 专家（股票分析师、行业分析师、市场分析师等）
- 长上下文对话，支持复杂投资场景分析
- 可自定义专家提示词和模型选择

### 2. 灵活的 AI 模型配置
- 支持多种 AI 服务提供商（阶跃星辰、Kimi、OpenAI 等）
- 用户可配置自己的 API Key
- 支持不同模型的切换和组合使用

### 3. 完整的数据分析能力
- 历史数据分析和技术指标计算
- 实时新闻和舆情分析
- 投资组合风险评估
- 市场情绪可视化

### 4. 现代化的技术栈
- 前端：React 18 + TypeScript + Tailwind CSS
- 后端：FastAPI + Python 3.9+
- 数据库：PostgreSQL
- AI 集成：支持多种大模型 API

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+（可选，也可使用 SQLite）

### 1. 克隆项目

```bash
git clone https://github.com/LeoLinFinance/QuantyWind.git
cd QuantyWind
```

### 2. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
# 数据库配置（可选，默认使用 SQLite）
DATABASE_URL=postgresql://user:password@localhost:5432/quantywind

# 数据源 API Keys（可选，用于获取市场数据）
ALPHA_VANTAGE_API_KEY=your_key_here
TWELVE_DATA_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# AI 模型配置（可选，也可在应用内配置）
# 留空则需要用户在设置页面配置自己的 API Key
STEPFUN_API_KEY=
KIMI_API_KEY=
```

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# （可选）初始化示例数据
python scripts/init_database.py
```

### 5. 启动后端服务

```bash
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 6. 安装前端依赖

```bash
cd ../
npm install
```

### 7. 启动前端开发服务器

```bash
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

### 8. 配置 AI 服务

访问 `http://localhost:3000/settings` 配置您的 AI API Key：

1. 选择服务提供商（阶跃星辰、Kimi 或 OpenAI）
2. 输入您的 API Key
3. 选择默认模型
4. 保存配置

## 🔑 获取 API Key

### AI 模型服务

- **阶跃星辰 (StepFun)**：访问 [platform.stepfun.com](https://platform.stepfun.com) 注册并获取
- **Kimi (月之暗面)**：访问 [platform.moonshot.cn](https://platform.moonshot.cn) 注册并获取
- **OpenAI**：访问 [platform.openai.com](https://platform.openai.com) 注册并获取

### 数据源服务（可选）

- **Alpha Vantage**：访问 [alphavantage.co](https://www.alphavantage.co/support/#api-key) 获取免费 API Key
- **Twelve Data**：访问 [twelvedata.com](https://twelvedata.com) 注册获取
- **NewsAPI**：访问 [newsapi.org](https://newsapi.org) 注册获取

## 📚 使用文档

### 智者论坛

智者论坛是核心功能，提供多专家 AI 对话：

1. 在输入框中描述您的投资问题或场景
2. 选择要咨询的专家（可多选）
3. 专家会基于您的持仓和市场情况给出建议
4. 支持连续对话，深入探讨

### 自定义专家

您可以在专家论坛页面自定义专家：

1. 点击"专家配置"按钮
2. 编辑专家的提示词
3. 选择使用的模型
4. 保存配置

### API 文档

启动后端服务后，访问 `http://localhost:8000/api/docs` 查看完整的 API 文档。

## 🏗️ 项目结构

```
quantywind/
├── backend/                 # 后端代码
│   ├── models/             # 数据模型
│   ├── routers/            # API 路由
│   ├── services/           # 业务逻辑
│   ├── middleware/         # 中间件
│   └── main.py            # 应用入口
├── src/                    # 前端代码
│   ├── components/        # React 组件
│   ├── pages/            # 页面组件
│   ├── contexts/         # React Context
│   └── App.tsx           # 应用入口
├── alembic/               # 数据库迁移
├── tests/                 # 测试代码
└── docs/                  # 文档
```

## 🔒 安全说明

- 所有 API Key 都经过加密存储
- 支持 HTTPS 和安全头部配置
- 提供 IP 白名单和访问控制
- 请妥善保管您的 API Key，不要提交到版本控制

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 开源协议

本项目采用 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚠️ 免责声明

本平台提供的所有分析和建议仅供参考，不构成投资建议。投资有风险，入市需谨慎。使用本平台进行投资决策的风险由用户自行承担。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://reactjs.org/) - 用户界面库
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- [阶跃星辰](https://www.stepfun.com/) - AI 模型服务
- [Kimi](https://www.moonshot.cn/) - AI 模型服务

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 Issue：[GitHub Issues](https://github.com/LeoLinFinance/QuantyWind/issues)

---

⭐ 如果这个项目对您有帮助，请给我们一个 Star！
