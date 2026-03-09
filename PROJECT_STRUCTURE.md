# 项目结构说明

```
滴答学术/
├── miniprogram/                    # 微信小程序前端
│   ├── pages/                      # 页面目录
│   │   ├── index/                  # 首页（文章列表）
│   │   │   ├── index.js           # 页面逻辑
│   │   │   ├── index.wxml         # 页面结构
│   │   │   └── index.wxss         # 页面样式
│   │   ├── detail/                 # 详情页（四层内容+AI问答）
│   │   │   ├── detail.js
│   │   │   ├── detail.wxml
│   │   │   └── detail.wxss
│   │   ├── search/                 # 搜索页
│   │   │   ├── search.js
│   │   │   └── search.wxml
│   │   └── favorites/              # 收藏页
│   │       ├── favorites.js
│   │       └── favorites.wxml
│   ├── images/                     # 图片资源（需自行添加）
│   ├── app.js                      # 小程序入口
│   ├── app.json                    # 小程序配置
│   └── project.config.json         # 项目配置
│
├── backend/                        # 后端服务
│   ├── models/                     # 数据模型
│   │   └── Article.js             # 文章模型
│   ├── routes/                     # API路由
│   │   ├── articles.js            # 文章接口
│   │   ├── chat.js                # AI聊天接口
│   │   ├── admin.js               # 管理接口
│   │   └── crawler.js             # 采集接口
│   ├── services/                   # 业务服务
│   │   └── aiService.js           # AI服务（Kimi/Claude）
│   ├── crawler/                    # 采集系统
│   │   ├── scheduler.js           # 调度器（每3小时）
│   │   ├── processor.js           # 内容处理器
│   │   └── sources/               # 采集源
│   │       ├── github.js          # GitHub采集
│   │       ├── huggingface.js     # HuggingFace采集
│   │       └── arxiv.js           # arXiv采集
│   ├── server.js                   # 服务器入口
│   ├── package.json               # 依赖配置
│   ├── .env.example               # 环境变量模板
│   └── .env                       # 环境变量（需创建）
│
├── docs/                           # 文档目录
│   ├── README.md                  # 项目说明
│   ├── QUICKSTART.md              # 快速开始
│   ├── ARCHITECTURE.md            # 架构文档
│   ├── DEPLOYMENT.md              # 部署指南
│   └── TODO.md                    # 任务清单
│
├── start.sh                        # 快速启动脚本
├── .gitignore                      # Git忽略配置
└── PROJECT_STRUCTURE.md            # 本文件

```

## 核心文件说明

### 小程序端

| 文件 | 说明 |
|------|------|
| `miniprogram/app.js` | 小程序全局配置，包含API地址 |
| `miniprogram/pages/index/` | 首页，展示分类和文章列表 |
| `miniprogram/pages/detail/` | 详情页，四层内容切换+音频播放+AI问答 |
| `miniprogram/pages/search/` | 搜索功能 |
| `miniprogram/pages/favorites/` | 收藏管理 |

### 后端服务

| 文件 | 说明 |
|------|------|
| `backend/server.js` | Express服务器入口 |
| `backend/models/Article.js` | 文章数据模型（四层结构） |
| `backend/routes/articles.js` | 文章CRUD接口 |
| `backend/routes/chat.js` | AI问答接口 |
| `backend/services/aiService.js` | AI服务封装（支持Kimi/Claude） |

### 采集系统

| 文件 | 说明 |
|------|------|
| `backend/crawler/scheduler.js` | 定时调度器（每3小时） |
| `backend/crawler/processor.js` | 内容处理：去重+AI生成+保存 |
| `backend/crawler/sources/github.js` | GitHub仓库采集 |
| `backend/crawler/sources/huggingface.js` | HuggingFace模型/Spaces采集 |
| `backend/crawler/sources/arxiv.js` | arXiv论文采集 |

## 数据流向

```
采集源 → 原始内容 → AI生成四层内容 → 保存数据库 → 小程序展示
  ↓
GitHub/HuggingFace/arXiv
  ↓
去重检查
  ↓
Kimi/Claude API
  ↓
MongoDB
  ↓
微信小程序
```

## 关键技术点

### 1. 四层内容结构
```javascript
layers: [
  { level: 'concept', content: '概念科普' },
  { level: 'principle', content: '技术原理' },
  { level: 'implementation', content: '代码实现' },
  { level: 'application', content: '行业应用' }
]
```

### 2. 去重机制
使用内容MD5哈希值进行去重：
```javascript
contentHash: crypto.createHash('md5').update(content).digest('hex')
```

### 3. 定时采集
使用node-cron实现每3小时采集：
```javascript
cron.schedule('0 */3 * * *', () => { ... })
```

### 4. AI交互
详情页内置AI问答窗口，基于文章上下文回答问题

## 扩展点

### 添加新的采集源
1. 在 `backend/crawler/sources/` 创建新文件
2. 实现 `crawl()` 方法
3. 在 `scheduler.js` 中注册

### 添加新的内容分类
1. 修改 `backend/models/Article.js` 的 category enum
2. 更新 `miniprogram/pages/index/index.js` 的 categories 数组
3. 调整采集器的分类映射

### 集成新的AI模型
1. 在 `backend/services/aiService.js` 添加新方法
2. 更新 `.env` 配置
3. 修改 `AI_PROVIDER` 环境变量

## 需要自行添加的资源

1. 小程序图标（`miniprogram/images/`）：
   - home.png / home-active.png
   - favorite.png / favorite-active.png
   - search.png
   - play.png / pause.png
   - share.png

2. 环境变量配置（`backend/.env`）

3. 微信小程序AppID（`miniprogram/project.config.json`）

## 开发建议

1. 先配置好所有API密钥
2. 测试单个采集源后再启用全部
3. 监控AI API调用成本
4. 定期备份MongoDB数据
5. 使用PM2管理生产环境进程
