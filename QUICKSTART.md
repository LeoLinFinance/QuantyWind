# 快速开始指南

## 前置要求

1. 安装Node.js (v16+)
2. 安装MongoDB (v4.4+)
3. 安装微信开发者工具
4. 准备API密钥：
   - Kimi API Key 或 Claude API Key
   - GitHub Token
   - HuggingFace Token（可选）

## 5分钟快速启动

### 1. 配置环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```env
MONGODB_URI=mongodb://localhost:27017/didaxueshu
PORT=3000
KIMI_API_KEY=your_kimi_api_key_here
GITHUB_TOKEN=your_github_token_here
```

### 2. 启动MongoDB

```bash
# macOS (使用Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
net start MongoDB
```

### 3. 启动后端服务

```bash
# 方式1：使用启动脚本（推荐）
./start.sh

# 方式2：手动启动
cd backend
npm install
npm start
```

### 4. 测试后端

访问 http://localhost:3000/health 应该看到：

```json
{
  "status": "ok",
  "timestamp": "2024-xx-xx..."
}
```

### 5. 配置小程序

1. 打开 `miniprogram/app.js`
2. 修改 `apiBase` 为你的后端地址（开发环境可用 `http://localhost:3000/api`）
3. 打开微信开发者工具
4. 导入项目，选择 `miniprogram` 目录
5. 填入你的AppID（测试可用测试号）

### 6. 运行小程序

在微信开发者工具中点击"编译"，即可看到小程序界面。

## 测试采集功能

### 手动触发一次采集

```bash
cd backend
node crawler/scheduler.js
```

观察控制台输出，应该能看到采集进度。

### 查看采集结果

```bash
# 使用MongoDB客户端
mongosh didaxueshu

# 查询文章数量
db.articles.countDocuments()

# 查看最新文章
db.articles.find().sort({createdAt: -1}).limit(1).pretty()
```

## 常见问题

### Q: MongoDB连接失败
A: 确保MongoDB服务已启动，检查连接字符串是否正确

### Q: AI生成失败
A: 检查API密钥是否正确，确认账户有足够额度

### Q: 小程序无法请求API
A: 
1. 开发环境：在微信开发者工具中勾选"不校验合法域名"
2. 生产环境：在小程序后台配置服务器域名白名单

### Q: 采集不到数据
A: 
1. 检查GitHub Token权限
2. 确认网络可以访问GitHub/HuggingFace/arXiv
3. 查看错误日志

## 下一步

- 阅读 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解系统架构
- 阅读 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解生产部署
- 查看 [TODO.md](./TODO.md) 了解开发计划

## 获取帮助

如遇到问题：
1. 查看控制台错误日志
2. 检查 `.env` 配置
3. 确认所有服务正常运行
4. 查看MongoDB日志

## 开发建议

1. 先用少量数据测试AI生成效果
2. 调整采集频率避免API限流
3. 定期备份数据库
4. 监控API调用成本
