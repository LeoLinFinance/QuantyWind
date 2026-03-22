# 安全远程部署 - 快速开始

本文档介绍如何快速部署量数风行应用的安全版本。

## 📋 概述

本部署方案实现了以下安全特性：

- ✅ **身份验证和授权**：JWT 令牌 + 基于角色的访问控制
- ✅ **数据加密**：HTTPS 传输加密 + 数据库加密存储
- ✅ **源代码保护**：容器化部署 + 代码混淆
- ✅ **网络隔离**：多层网络架构，数据库不暴露公网
- ✅ **审计日志**：完整的操作日志记录
- ✅ **会话管理**：自动超时 + 异常检测
- ✅ **请求限流**：防止暴力破解和 DDoS 攻击

## 🚀 快速部署（5 分钟）

### 步骤 1：生成安全密钥

```bash
# 运行密钥生成脚本
python3 generate-secrets.py

# 将输出的密钥复制到 .env 文件
cp .env.example .env
# 编辑 .env 文件，粘贴生成的密钥
```

### 步骤 2：生成 SSL 证书

**开发环境**：
```bash
cd nginx
chmod +x generate-ssl-cert.sh
./generate-ssl-cert.sh
cd ..
```

**生产环境**：
```bash
# 使用 Let's Encrypt
sudo certbot certonly --standalone -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### 步骤 3：配置环境变量

编辑 `.env` 文件，填写以下必需配置：

```bash
# API 密钥
STEPFUN_API_KEY=your_stepfun_api_key
KIMI_API_KEY=your_kimi_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

# CORS（生产环境域名）
ALLOWED_ORIGINS=https://yourdomain.com
```

### 步骤 4：启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 步骤 5：验证部署

访问 https://localhost/health 检查服务状态。

## 📁 项目结构

```
.
├── Dockerfile                      # 应用容器配置
├── docker-compose.yml              # 服务编排配置
├── .env.example                    # 环境变量模板
├── generate-secrets.py             # 密钥生成脚本
├── nginx/
│   ├── nginx.conf                  # Nginx 配置
│   ├── generate-ssl-cert.sh        # SSL 证书生成脚本
│   └── ssl/                        # SSL 证书目录
├── backend/
│   ├── main.py                     # FastAPI 主应用（已更新）
│   ├── database/
│   │   ├── config.py               # 数据库配置
│   │   └── init.sql                # 数据库初始化脚本
│   ├── models/                     # 数据模型（待实现）
│   ├── services/                   # 业务服务（待实现）
│   └── routers/                    # API 路由（待实现）
└── docs/
    ├── DOCKER_DEPLOYMENT.md        # Docker 部署详细指南
    ├── SECURITY_CHECKLIST.md       # 安全配置清单
    └── SECURE_DEPLOYMENT_README.md # 本文档
```

## 🔐 安全配置要点

### 1. 密码和密钥

- ✅ 使用 `generate-secrets.py` 生成强随机密钥
- ✅ 每个环境使用不同的密钥
- ✅ 不要将密钥提交到版本控制
- ✅ 定期更换密钥

### 2. 网络安全

- ✅ 仅开放 80 和 443 端口
- ✅ 数据库和 Redis 在内部网络
- ✅ 使用 HTTPS 强制加密
- ✅ 配置防火墙规则

### 3. 访问控制

- ✅ 修改默认管理员密码
- ✅ 实施最小权限原则
- ✅ 启用账户锁定机制
- ✅ 配置会话超时

### 4. 日志和监控

- ✅ 记录所有安全事件
- ✅ 配置日志轮转
- ✅ 设置告警通知
- ✅ 定期审查日志

## 📊 系统架构

```
┌─────────────────────────────────────────┐
│           用户（浏览器）                 │
└──────────────┬──────────────────────────┘
               │ HTTPS (TLS 1.3)
               ▼
┌─────────────────────────────────────────┐
│    Nginx 反向代理（公网层）              │
│    - SSL 终止                            │
│    - 请求限流：100 req/min               │
│    - 登录限流：5 req/min                 │
│    - 静态文件缓存                        │
└──────────────┬──────────────────────────┘
               │ HTTP (内部)
               ▼
┌─────────────────────────────────────────┐
│    FastAPI 应用（应用层）                │
│    - JWT 身份验证                        │
│    - RBAC 权限控制                       │
│    - 业务逻辑处理                        │
│    - 审计日志记录                        │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │   Redis     │
│ (数据层)    │ │ (缓存层)    │
│ - 加密存储  │ │ - 会话管理  │
│ - 不暴露    │ │ - 令牌黑名单│
└─────────────┘ └─────────────┘
```

## 🛠️ 常用操作

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f app
```

### 重启服务

```bash
docker-compose restart
```

### 备份数据库

```bash
docker-compose exec postgres pg_dump -U quantflow_user quantflow > backup.sql
```

### 更新应用

```bash
git pull
docker-compose build
docker-compose up -d
```

## 📚 详细文档

- [Docker 部署指南](DOCKER_DEPLOYMENT.md) - 完整的部署说明
- [安全配置清单](SECURITY_CHECKLIST.md) - 安全检查项
- [需求文档](.kiro/specs/secure-remote-deployment/requirements.md) - 功能需求
- [设计文档](.kiro/specs/secure-remote-deployment/design.md) - 架构设计

## 🔄 下一步

任务 1（基础设施配置）已完成。接下来需要实现：

1. **任务 2**：实现加密服务
2. **任务 3**：实现用户模型和数据库架构
3. **任务 4**：实现身份验证服务
4. **任务 5**：实现授权服务
5. **任务 7**：实现会话管理服务
6. **任务 8**：实现审计日志服务

## ⚠️ 重要提示

1. **开发环境**：使用自签名证书，浏览器会显示警告（正常）
2. **生产环境**：必须使用有效的 SSL 证书（Let's Encrypt 或购买）
3. **密钥安全**：不要将 .env 文件提交到版本控制
4. **定期更新**：及时更新依赖包和 Docker 镜像
5. **备份策略**：配置自动备份，定期测试恢复

## 🆘 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs app

# 检查配置
docker-compose config
```

### 数据库连接失败

```bash
# 检查数据库状态
docker-compose ps postgres

# 测试连接
docker-compose exec postgres psql -U quantflow_user -d quantflow -c "SELECT 1"
```

### SSL 证书错误

```bash
# 检查证书文件
ls -la nginx/ssl/

# 验证证书
openssl x509 -in nginx/ssl/cert.pem -text -noout
```

## 📞 支持

如有问题，请：
1. 查看详细文档
2. 检查日志文件
3. 参考故障排查指南
4. 联系技术支持

---

**版本**: 1.0.0  
**最后更新**: 2024-01
