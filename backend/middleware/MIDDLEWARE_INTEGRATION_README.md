# 中间件集成文档

## 概述

本文档描述了量数风行应用中集成的所有安全中间件，包括它们的功能、配置和执行顺序。

## 中间件列表

### 1. SecurityHeadersMiddleware（安全头部中间件）

**功能**：为所有 HTTP 响应添加安全相关的头部

**添加的头部**：
- `Strict-Transport-Security` (HSTS) - 强制使用 HTTPS
- `Content-Security-Policy` (CSP) - 内容安全策略
- `X-Content-Type-Options` - 防止 MIME 类型嗅探
- `X-Frame-Options` - 防止点击劫持
- `X-XSS-Protection` - XSS 保护
- `Referrer-Policy` - Referrer 策略
- `Permissions-Policy` - 权限策略

**配置**：
```python
app.add_middleware(
    SecurityHeadersMiddleware,
    hsts_max_age=31536000,  # 1 年
    csp_policy="default-src 'self'; ..."
)
```

**验证需求**：5.1, 5.5

### 2. HTTPSRedirectMiddleware（HTTPS 重定向中间件）

**功能**：将所有 HTTP 请求重定向到 HTTPS

**特性**：
- 可通过环境变量 `ENABLE_HTTPS_REDIRECT` 启用/禁用
- 支持排除特定路径（如健康检查端点）
- 检查 `X-Forwarded-Proto` 头部以支持反向代理

**配置**：
```python
if ENABLE_HTTPS_REDIRECT:
    app.add_middleware(
        HTTPSRedirectMiddleware,
        enabled=True,
        exclude_paths={"/health", "/"}
    )
```

**环境变量**：
- `ENABLE_HTTPS_REDIRECT=true` - 启用 HTTPS 重定向（生产环境推荐）

**验证需求**：5.1

### 3. RequestLoggingMiddleware（请求日志中间件）

**功能**：记录所有 HTTP 请求的详细信息

**记录内容**：
- 请求方法、路径、查询参数
- 客户端 IP 地址（支持反向代理）
- User-Agent
- 响应状态码
- 处理时间

**特性**：
- 添加 `X-Process-Time` 响应头部
- 支持排除特定路径（如健康检查）
- 自动记录错误和异常

**配置**：
```python
app.add_middleware(
    RequestLoggingMiddleware,
    log_request_body=False,  # 不记录请求体（可能包含敏感信息）
    log_response_body=False,  # 不记录响应体（可能很大）
    exclude_paths={"/health", "/metrics"}
)
```

**验证需求**：7.1, 7.2

### 4. IPWhitelistMiddleware（IP 白名单中间件）

**功能**：限制只有白名单中的 IP 地址才能访问特定端点

**特性**：
- 可通过环境变量启用/禁用
- 支持配置受保护的路径前缀
- 自动记录违规访问尝试

**配置**：
```python
if ENABLE_IP_WHITELIST and IP_WHITELIST:
    app.add_middleware(
        IPWhitelistMiddleware,
        whitelist=IP_WHITELIST,
        protected_paths={"/api/admin", "/api/audit"},
        enabled=True
    )
```

**环境变量**：
- `ENABLE_IP_WHITELIST=true` - 启用 IP 白名单
- `IP_WHITELIST=127.0.0.1,192.168.1.100` - 允许的 IP 地址列表（逗号分隔）

**验证需求**：9.1

### 5. CORSMiddleware（CORS 中间件）

**功能**：处理跨域资源共享（CORS）

**配置**：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
```

**环境变量**：
- `ALLOWED_ORIGINS=http://localhost:3000,https://example.com` - 允许的源列表（逗号分隔）

## 中间件执行顺序

中间件按照添加顺序的**相反顺序**执行（后添加的先执行）。

### 请求处理流程（从外到内）：

```
1. SecurityHeadersMiddleware     ← 最外层，确保所有响应都有安全头部
   ↓
2. HTTPSRedirectMiddleware       ← 强制 HTTPS（如果启用）
   ↓
3. RequestLoggingMiddleware      ← 记录请求日志
   ↓
4. IPWhitelistMiddleware         ← IP 白名单控制（如果启用）
   ↓
5. CORSMiddleware                ← CORS 处理
   ↓
6. 应用路由处理                  ← 最内层，处理实际业务逻辑
```

### 响应处理流程（从内到外）：

```
6. 应用路由处理                  ← 生成响应
   ↓
5. CORSMiddleware                ← 添加 CORS 头部
   ↓
4. IPWhitelistMiddleware         ← （已在请求阶段处理）
   ↓
3. RequestLoggingMiddleware      ← 添加 X-Process-Time 头部，记录日志
   ↓
2. HTTPSRedirectMiddleware       ← （已在请求阶段处理）
   ↓
1. SecurityHeadersMiddleware     ← 添加安全头部
   ↓
   返回给客户端
```

## 环境变量配置

在 `.env` 文件中配置以下环境变量：

```bash
# 环境类型
ENVIRONMENT=production

# CORS 配置
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# HTTPS 重定向（生产环境推荐启用）
ENABLE_HTTPS_REDIRECT=true

# IP 白名单（可选，用于保护管理端点）
ENABLE_IP_WHITELIST=false
IP_WHITELIST=127.0.0.1,192.168.1.100
```

## 健康检查端点

应用提供了增强的健康检查端点：

```
GET /health
```

**响应示例**：
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:45.123456",
  "middleware": {
    "security_headers": true,
    "https_redirect": true,
    "request_logging": true,
    "ip_whitelist": false,
    "cors": true
  }
}
```

## 测试

运行中间件集成测试：

```bash
python3 -m pytest tests/test_middleware_integration.py -v
```

测试覆盖：
- ✅ 安全头部存在性和正确性
- ✅ HTTPS 重定向功能
- ✅ 请求日志记录
- ✅ IP 白名单控制
- ✅ CORS 配置
- ✅ 中间件执行顺序
- ✅ 错误处理

## 安全最佳实践

### 生产环境配置

1. **启用 HTTPS 重定向**：
   ```bash
   ENABLE_HTTPS_REDIRECT=true
   ```

2. **配置严格的 CORS**：
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **启用 IP 白名单保护管理端点**（可选）：
   ```bash
   ENABLE_IP_WHITELIST=true
   IP_WHITELIST=your.office.ip.address
   ```

4. **禁用 API 文档**：
   - 在生产环境中，FastAPI 会自动禁用 `/api/docs` 和 `/api/redoc`

### 开发环境配置

1. **禁用 HTTPS 重定向**：
   ```bash
   ENABLE_HTTPS_REDIRECT=false
   ```

2. **允许本地源**：
   ```bash
   ALLOWED_ORIGINS=http://localhost:3000
   ```

3. **禁用 IP 白名单**：
   ```bash
   ENABLE_IP_WHITELIST=false
   ```

## 监控和日志

### 日志级别

中间件使用 Python 标准日志库，日志级别：
- `INFO` - 正常请求和响应
- `WARNING` - 安全违规（如 IP 白名单违规）
- `ERROR` - 请求处理错误

### 日志格式

```
2024-01-15 10:30:45 - backend.middleware.security_middleware - INFO - Request started: GET /api/data from 192.168.1.100 (Mozilla/5.0...)
2024-01-15 10:30:45 - backend.middleware.security_middleware - INFO - Request completed: GET /api/data status=200 time=0.0234s ip=192.168.1.100
```

### 监控指标

通过 `X-Process-Time` 响应头部可以监控请求处理时间：

```bash
curl -I https://yourdomain.com/api/data
# X-Process-Time: 0.0234
```

## 故障排查

### 问题：CORS 错误

**症状**：浏览器控制台显示 CORS 错误

**解决方案**：
1. 检查 `ALLOWED_ORIGINS` 环境变量是否包含前端域名
2. 确保前端使用的协议（http/https）与配置匹配
3. 检查是否包含端口号（如 `http://localhost:3000`）

### 问题：HTTPS 重定向循环

**症状**：浏览器显示"重定向次数过多"

**解决方案**：
1. 如果在反向代理后面，确保代理设置了 `X-Forwarded-Proto` 头部
2. 检查 Nginx 配置是否正确设置了 `proxy_set_header X-Forwarded-Proto $scheme;`
3. 在开发环境中禁用 HTTPS 重定向

### 问题：IP 白名单阻止合法访问

**症状**：返回 403 Forbidden

**解决方案**：
1. 检查 `IP_WHITELIST` 环境变量是否包含客户端 IP
2. 如果在反向代理后面，确保代理设置了 `X-Forwarded-For` 或 `X-Real-IP` 头部
3. 检查日志以确认实际的客户端 IP 地址

## 相关文档

- [认证中间件文档](./AUTH_MIDDLEWARE_README.md)
- [安全配置清单](../../SECURITY_CHECKLIST.md)
- [部署指南](../../DEPLOYMENT.md)

## 更新日志

### 2024-01-15
- ✅ 创建 SecurityHeadersMiddleware
- ✅ 创建 HTTPSRedirectMiddleware
- ✅ 创建 RequestLoggingMiddleware
- ✅ 创建 IPWhitelistMiddleware
- ✅ 集成所有中间件到 main.py
- ✅ 增强健康检查端点
- ✅ 创建完整的集成测试套件
- ✅ 所有测试通过（19/19）
