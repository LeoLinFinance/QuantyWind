# 部署指南

## 环境要求
- Node.js 16+
- MongoDB 4.4+
- 微信开发者工具

## 后端部署

### 1. 安装依赖
```bash
cd backend
npm install
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env` 并填写配置：
```bash
cp .env.example .env
```

必填配置：
- `MONGODB_URI`: MongoDB连接地址
- `KIMI_API_KEY` 或 `CLAUDE_API_KEY`: AI服务密钥
- `GITHUB_TOKEN`: GitHub访问令牌
- `HUGGINGFACE_TOKEN`: HuggingFace访问令牌（可选）

### 3. 启动服务
```bash
# 开发环境
npm run dev

# 生产环境
npm start
```

### 4. 启动采集器
```bash
npm run crawler
```

## 小程序部署

### 1. 配置API地址
修改 `miniprogram/app.js` 中的 `apiBase` 为你的后端地址

### 2. 导入项目
1. 打开微信开发者工具
2. 导入项目，选择 `miniprogram` 目录
3. 填写AppID

### 3. 上传代码
1. 点击"上传"按钮
2. 填写版本号和备注
3. 提交审核

## 服务器部署建议

### 使用PM2管理进程
```bash
npm install -g pm2

# 启动后端
pm2 start backend/server.js --name didaxueshu-api

# 启动采集器
pm2 start backend/crawler/scheduler.js --name didaxueshu-crawler

# 查看日志
pm2 logs

# 设置开机自启
pm2 startup
pm2 save
```

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 监控和维护

### 日志查看
```bash
# PM2日志
pm2 logs

# MongoDB日志
tail -f /var/log/mongodb/mongod.log
```

### 数据备份
```bash
# 备份MongoDB
mongodump --uri="mongodb://localhost:27017/didaxueshu" --out=/backup/$(date +%Y%m%d)
```

### 性能监控
- 使用PM2监控CPU和内存使用
- 配置MongoDB慢查询日志
- 设置告警通知（邮件/微信）

## 常见问题

### 采集失败
- 检查API Token是否有效
- 检查网络连接
- 查看错误日志

### AI生成失败
- 检查API密钥配置
- 确认API额度充足
- 查看错误响应

### 小程序审核不通过
- 确保内容合规
- 添加用户协议和隐私政策
- 完善小程序信息
