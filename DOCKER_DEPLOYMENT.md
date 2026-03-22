# Docker 部署指南

本指南介绍如何使用 Docker 和 Docker Compose 部署量数风行应用。

## 前置要求

- Docker 20.10 或更高版本
- Docker Compose 2.0 或更高版本
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

## 快速开始

### 1. 配置环境变量

复制环境变量模板并填写实际值：

```bash
cp .env.example .env
```

编辑 `.env` 文件，**必须修改**以下关键配置：

```bash
# 数据库密码（强密码，至少 16 字符）
POSTGRES_PASSWORD=your_strong_password_here

# Redis 密码（强密码）
REDIS_PASSWORD=your_redis_password_here

# 应用密钥（使用以下命令生成）
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_generated_secret_key
JWT_SECRET_KEY=your_generated_jwt_secret_key
ENCRYPTION_KEY=your_generated_encryption_key

# CORS 允许的源（生产环境域名）
ALLOWED_ORIGINS=https://yourdomain.com

# API 密钥
STEPFUN_API_KEY=your_stepfun_api_key
KIMI_API_KEY=your_kimi_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

### 2. 生成 SSL 证书

**开发环境**（自签名证书）：

```bash
cd nginx
chmod +x generate-ssl-cert.sh
./generate-ssl-cert.sh
cd ..
```

**生产环境**（Let's Encrypt）：

```bash
# 安装 certbot
sudo apt-get install certbot

# 生成证书
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书到 nginx/ssl 目录
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### 3. 构建和启动服务

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 验证部署

访问以下 URL 验证服务是否正常运行：

- **健康检查**: https://localhost/health
- **API 文档**（仅开发环境）: https://localhost/api/docs
- **前端应用**: https://localhost/

## 服务架构

```
┌─────────────────────────────────────────┐
│           互联网（HTTPS）                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Nginx 反向代理（端口 80/443）         │
│    - SSL 终止                            │
│    - 请求限流                            │
│    - 静态文件服务                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    FastAPI 应用（端口 8000）             │
│    - 业务逻辑                            │
│    - API 端点                            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │   Redis     │
│ (端口 5432) │ │ (端口 6379) │
└─────────────┘ └─────────────┘
```

## 网络隔离

系统使用两个独立的 Docker 网络：

1. **app_network**（公网层）
   - Nginx 和 FastAPI 应用
   - 可访问外网

2. **data_network**（数据层）
   - FastAPI 应用、PostgreSQL 和 Redis
   - 内部网络，不可访问外网
   - 数据库不直接暴露到公网

## 常用命令

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
docker-compose logs -f nginx
docker-compose logs -f postgres
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart app
```

### 停止服务

```bash
# 停止所有服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷（警告：会删除所有数据）
docker-compose down -v
```

### 进入容器

```bash
# 进入应用容器
docker-compose exec app bash

# 进入数据库容器
docker-compose exec postgres psql -U quantflow_user -d quantflow
```

### 数据库操作

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U quantflow_user quantflow > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U quantflow_user quantflow < backup.sql
```

## 更新应用

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d

# 4. 查看日志确认启动成功
docker-compose logs -f app
```

## 性能优化

### 调整资源限制

编辑 `docker-compose.yml`，为服务添加资源限制：

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 调整数据库连接池

编辑 `backend/database/config.py`：

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,      # 增加连接池大小
    max_overflow=40,   # 增加最大溢出连接数
)
```

## 监控和日志

### 查看容器资源使用

```bash
docker stats
```

### 日志轮转

Docker 默认会无限制地保存日志，建议配置日志轮转：

编辑 `docker-compose.yml`，为每个服务添加：

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 安全检查清单

- [ ] 已修改所有默认密码
- [ ] 已生成强随机密钥
- [ ] 已配置正确的 CORS 源
- [ ] 已使用有效的 SSL 证书（生产环境）
- [ ] 数据库不直接暴露到公网
- [ ] 已配置防火墙规则
- [ ] 已启用日志记录
- [ ] 已设置定期备份

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs app

# 检查配置文件
docker-compose config
```

### 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps postgres

# 测试数据库连接
docker-compose exec postgres psql -U quantflow_user -d quantflow -c "SELECT 1"
```

### SSL 证书错误

```bash
# 检查证书文件是否存在
ls -la nginx/ssl/

# 验证证书有效性
openssl x509 -in nginx/ssl/cert.pem -text -noout
```

### 端口冲突

如果端口 80 或 443 已被占用，编辑 `docker-compose.yml` 修改端口映射：

```yaml
services:
  nginx:
    ports:
      - "8080:80"
      - "8443:443"
```

## 生产环境建议

1. **使用外部数据库**：考虑使用托管的 PostgreSQL 服务（如 AWS RDS）
2. **使用 Redis 集群**：提高缓存可用性
3. **配置负载均衡**：使用多个应用实例
4. **启用自动备份**：定期备份数据库和配置
5. **配置监控告警**：使用 Prometheus + Grafana
6. **使用 CDN**：加速静态资源访问
7. **定期更新**：及时更新依赖包和 Docker 镜像

## 支持

如有问题，请查看：
- [故障排查指南](TROUBLESHOOTING.md)
- [安全配置清单](SECURITY_CHECKLIST.md)
- [用户管理指南](USER_MANAGEMENT.md)
