# 快速开始指南

本指南将帮助您在 5 分钟内启动量数风行平台。

## 前置要求

- Python 3.9+
- Node.js 16+
- Git

## 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/quantywind.git
cd quantywind
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件（可选，也可以在应用内配置）：

```env
# 留空，稍后在应用设置页面配置
STEPFUN_API_KEY=
KIMI_API_KEY=
```

### 3. 启动后端（终端 1）

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 初始化数据库
alembic upgrade head

# 启动服务
python main.py
```

后端将在 `http://localhost:8000` 启动

### 4. 启动前端（终端 2）

```bash
# 在项目根目录
npm install
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 5. 配置 API Key

1. 访问 `http://localhost:3000/settings`
2. 点击"添加 API Key"
3. 选择服务商（推荐：阶跃星辰）
4. 输入您的 API Key
5. 保存

### 6. 开始使用

访问 `http://localhost:3000/expert-forum` 开始与 AI 专家对话！

## 获取 API Key

### 阶跃星辰（推荐，国内访问快）

1. 访问 [platform.stepfun.com](https://platform.stepfun.com)
2. 注册账号
3. 在控制台创建 API Key
4. 新用户通常有免费额度

### Kimi（支持在线搜索）

1. 访问 [platform.moonshot.cn](https://platform.moonshot.cn)
2. 注册账号
3. 在控制台创建 API Key
4. 新用户通常有免费额度

## 常见问题

### Q: 后端启动失败？

A: 检查 Python 版本和依赖安装：

```bash
python --version  # 应该是 3.9+
pip list | grep fastapi
```

### Q: 前端无法连接后端？

A: 确认后端在 8000 端口运行：

```bash
curl http://localhost:8000/health
```

### Q: AI 功能不可用？

A: 检查是否配置了 API Key：

1. 访问设置页面
2. 确认 API Key 已添加且状态为"启用"
3. 查看浏览器控制台和后端日志

### Q: 数据库错误？

A: 重新初始化数据库：

```bash
cd backend
rm -f data/*.db  # 删除旧数据库（如果使用 SQLite）
alembic upgrade head
```

## 下一步

- 📖 阅读完整 [README](README.md)
- 🎯 查看[功能文档](docs/)
- 🤝 参与[贡献](CONTRIBUTING.md)
- 💬 加入社区讨论

## 需要帮助？

- 提交 [Issue](https://github.com/yourusername/quantywind/issues)
- 查看 [FAQ](docs/FAQ.md)
- 发送邮件：your.email@example.com

---

祝您使用愉快！如果觉得有帮助，请给我们一个 ⭐
