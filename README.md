# 🎓 滴答学术 - AI技术播客平台

一个基于AI驱动的技术播客平台，提供深度的AI技术内容解读。

## ✨ 功能特点

- 📚 **4层内容结构**：概念 → 原理 → 实现 → 应用
- 🤖 **AI驱动生成**：使用StepFun API生成高质量内容
- 🎯 **4大专业领域**：AI世界模型、具身智能、脑机接口、芯片架构
- 📊 **49篇精选文章**：每篇8000+字深度解读
- 🔗 **原文链接**：直接跳转到arXiv论文原文
- 💻 **响应式设计**：优雅的渐变UI，流畅的交互体验

## 🚀 快速开始

### 本地运行

```bash
# 1. 安装依赖
cd backend
npm install

# 2. 启动后端服务
node production-server.js

# 3. 启动Web服务器（新终端）
cd demo-web
python3 -m http.server 8080

# 4. 访问网站
# 打开浏览器访问: http://localhost:8080/index-fixed.html
```

### 查看效果

- 🌐 Web演示：http://localhost:8080/index-fixed.html
- 🔌 后端API：http://localhost:3000/api

## 📦 技术栈

### 后端
- Node.js + Express
- SQLite数据库
- StepFun AI API（阶跃星辰）
- Better-sqlite3

### 前端
- 纯HTML/CSS/JavaScript
- 响应式设计
- 渐变UI设计
- 模态框交互

### 数据源
- arXiv论文
- GitHub项目
- HuggingFace模型

## 🎯 发布网站

我们为你准备了3种发布方案：

### 方案1：GitHub Pages（推荐）
- ✅ 完全免费
- ✅ 10分钟部署
- ✅ 自动HTTPS
- 📖 查看：[网站发布完全指南.md](网站发布完全指南.md)

### 方案2：Vercel + Railway
- ✅ 低成本（$5-20/月）
- ✅ 完整功能
- ✅ 自动部署
- 📖 查看：[快速部署指南.md](快速部署指南.md)

### 方案3：云服务器
- ✅ 完全控制
- ✅ 高性能
- ✅ 可定制
- 📖 查看：[发布指南.md](发布指南.md)

## 📊 项目状态

### 数据统计
- 📝 文章总数：49篇
- 🏷️ 分类分布：
  - AI世界模型：19篇
  - 脑机接口：14篇
  - 芯片架构：9篇
  - 具身智能：7篇

### 内容质量
- ✅ 所有文章格式正确
- ✅ 4层内容完整
- ✅ 平均8000+字/篇
- ✅ 中英文混合专业术语

## 📁 项目结构

```
.
├── backend/                    # 后端服务
│   ├── crawler/               # 数据采集器
│   │   ├── sources/          # 数据源（arXiv, GitHub等）
│   │   ├── collect-with-real-ai.js  # AI内容生成
│   │   └── processor.js      # 内容处理
│   ├── services/             # 业务服务
│   │   └── aiService.js      # AI服务集成
│   ├── data/                 # 数据库
│   │   └── didaxueshu.db     # SQLite数据库
│   ├── production-server.js  # 生产服务器
│   ├── database.js           # 数据库操作
│   └── export-static.js      # 静态数据导出
├── demo-web/                  # Web前端
│   ├── index-fixed.html      # 主页面（动态版）
│   ├── index-static.html     # 静态版本
│   └── data.json             # 导出的静态数据
├── miniprogram/               # 微信小程序
│   └── pages/                # 小程序页面
├── 网站发布完全指南.md        # 发布指南（推荐阅读）
├── 快速部署指南.md            # 快速部署
├── 发布指南.md                # 详细发布说明
└── PROJECT_SUMMARY.md         # 项目总结
```

## 🔧 开发指南

### 生成新文章

```bash
cd backend/crawler
node collect-with-real-ai.js
```

### 导出静态数据

```bash
cd backend
node export-static.js
```

### 修复内容格式

```bash
cd backend
node fix-content.js
```

## 📚 文档索引

| 文档 | 说明 | 推荐阅读 |
|------|------|---------|
| [网站发布完全指南.md](网站发布完全指南.md) | 完整发布指南 | ⭐⭐⭐⭐⭐ |
| [快速部署指南.md](快速部署指南.md) | 快速上手 | ⭐⭐⭐⭐ |
| [发布指南.md](发布指南.md) | 详细说明 | ⭐⭐⭐ |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目概览 | ⭐⭐⭐ |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 问题排查 | ⭐⭐ |

## 🎨 界面预览

### 主页
- 渐变紫色背景
- 4个分类导航
- 卡片式文章列表
- 圆形查看按钮

### 文章详情
- 模态框展示
- 4个层级标签（概念、原理、实现、应用）
- 清晰的内容排版
- 可点击的标题链接

## 🔑 环境变量

创建 `backend/.env` 文件：

```env
# StepFun API配置
STEPFUN_API_KEY=yFhYNndvjBoIjIkFqhUQfeN16XS7IREg8pwtGLaF5LoqSrnJDTgxWY0XomNZx8Na
STEPFUN_API_URL=https://api.stepfun.com/v1/chat/completions
STEPFUN_MODEL=step-1-32k

# 服务器配置
PORT=3000
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🎉 开始使用

1. **本地测试**：按照"快速开始"运行
2. **发布网站**：阅读[网站发布完全指南.md](网站发布完全指南.md)
3. **遇到问题**：查看[TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**立即开始你的AI技术播客平台之旅！** 🚀
