# 用户管理路由实现文档

## 概述

本文档描述了用户管理路由（`backend/routers/users.py`）的实现，该路由提供了完整的用户管理功能，包括用户列表查询、用户详情获取、角色更新和用户删除。

## 功能特性

### 1. 获取用户列表 (GET /api/users)

**权限要求**: 仅管理员

**功能**:
- 分页查询用户列表
- 支持按角色过滤
- 支持按激活状态过滤
- 记录审计日志

**请求参数**:
- `page`: 页码（默认 1，最小 1）
- `page_size`: 每页数量（默认 20，范围 1-100）
- `role`: 角色过滤（可选，值：viewer/user/admin）
- `is_active`: 激活状态过滤（可选，值：true/false）

**响应示例**:
```json
{
  "users": [
    {
      "id": "user-uuid",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "user",
      "is_active": true,
      "is_locked": false,
      "last_login": "2024-01-15T10:30:00",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

### 2. 获取用户详情 (GET /api/users/{user_id})

**权限要求**: 
- 用户可以查看自己的信息
- 管理员可以查看任何用户的信息

**功能**:
- 获取指定用户的详细信息
- 权限检查（自己或管理员）
- 记录审计日志

**响应示例**:
```json
{
  "id": "user-uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "is_locked": false,
  "last_login": "2024-01-15T10:30:00",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 3. 更新用户角色 (PUT /api/users/{user_id}/role)

**权限要求**: 仅管理员

**功能**:
- 更新指定用户的角色
- 防止管理员修改自己的角色
- 验证角色有效性
- 记录审计日志和安全事件

**请求体**:
```json
{
  "role": "admin"
}
```

**有效角色**: viewer, user, admin

**响应示例**:
```json
{
  "success": true,
  "message": "用户角色已从 user 更新为 admin",
  "user": {
    "id": "user-uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "admin",
    "is_active": true,
    "is_locked": false,
    "last_login": "2024-01-15T10:30:00",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 4. 删除用户 (DELETE /api/users/{user_id})

**权限要求**: 仅管理员

**功能**:
- 软删除用户（标记为非激活）
- 防止管理员删除自己
- 记录审计日志和安全事件

**响应示例**:
```json
{
  "success": true,
  "message": "用户 john_doe 已被停用"
}
```

## 安全特性

### 1. 认证和授权

- **JWT 令牌验证**: 所有端点都需要有效的 JWT 令牌
- **角色检查**: 管理员端点验证用户是否具有 admin 角色
- **自我访问控制**: 用户只能查看自己的信息（除非是管理员）

### 2. 审计日志

所有操作都会记录审计日志：

- **授权日志**: 记录权限检查结果
  - 用户 ID
  - 资源（user_management）
  - 操作（read/write/delete）
  - 是否授权
  - 原因

- **安全事件日志**: 记录重要的安全事件
  - 角色变更（严重程度：medium）
  - 用户删除（严重程度：high）
  - 包含详细的元数据

### 3. 输入验证

- **分页参数验证**: 
  - page >= 1
  - 1 <= page_size <= 100
- **角色验证**: 只接受 viewer/user/admin
- **用户存在性检查**: 操作前验证用户是否存在

### 4. 业务规则保护

- **防止自我修改**: 管理员不能修改或删除自己的账户
- **软删除**: 删除操作只是标记为非激活，不真正删除数据
- **权限隔离**: 普通用户无法访问管理功能

## 集成说明

### 1. 注册路由

在 `backend/main.py` 中注册路由：

```python
from backend.routers import users

app.include_router(users.router, tags=["users"])
```

### 2. 依赖项

路由依赖以下服务：

- `AuthenticationService`: JWT 令牌验证
- `AuthorizationService`: 权限检查和角色管理
- `AuditLogService`: 审计日志记录
- `get_current_user`: 中间件依赖项，提取当前用户信息

### 3. 数据库模型

使用以下模型：

- `User`: 用户模型（backend/models/user.py）
- `AuditLog`: 审计日志模型（backend/models/audit_log.py）

## 测试

### 运行测试

**前提条件**: Redis 服务必须运行

```bash
# 启动 Redis（如果未运行）
redis-server

# 运行测试
python3 -m pytest tests/test_users_router_standalone.py -v
```

### 测试覆盖

测试文件 `tests/test_users_router_standalone.py` 包含以下测试：

1. **获取用户列表测试**
   - 管理员可以获取用户列表
   - 普通用户无法获取用户列表

2. **获取用户详情测试**
   - 管理员可以获取任何用户的详情
   - 普通用户可以获取自己的详情
   - 普通用户无法获取其他用户的详情

3. **更新用户角色测试**
   - 管理员可以更新用户角色
   - 无效角色被拒绝
   - 管理员不能修改自己的角色

4. **删除用户测试**
   - 管理员可以删除用户（软删除）
   - 管理员不能删除自己
   - 验证用户被标记为非激活

### 手动测试

使用 curl 或 Postman 进行手动测试：

```bash
# 1. 登录获取令牌
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'

# 2. 获取用户列表
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 获取用户详情
curl -X GET http://localhost:8000/api/users/USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. 更新用户角色
curl -X PUT http://localhost:8000/api/users/USER_ID/role \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'

# 5. 删除用户
curl -X DELETE http://localhost:8000/api/users/USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 错误处理

### 常见错误响应

1. **401 Unauthorized**: 未提供令牌或令牌无效
```json
{
  "detail": "未授权访问"
}
```

2. **403 Forbidden**: 权限不足
```json
{
  "detail": "此操作需要管理员权限"
}
```

3. **404 Not Found**: 用户不存在
```json
{
  "detail": "用户 user-id 不存在"
}
```

4. **400 Bad Request**: 请求参数无效
```json
{
  "detail": "无效的角色。有效角色：viewer, user, admin"
}
```

5. **422 Unprocessable Entity**: 参数验证失败
```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

## 性能考虑

### 1. 分页

- 默认每页 20 条记录
- 最大每页 100 条记录
- 避免一次性加载大量数据

### 2. 数据库查询优化

- 使用索引字段（username, email）进行查询
- 只查询需要的字段
- 使用 SQLAlchemy 的 lazy loading

### 3. 审计日志

- 异步记录日志（不阻塞主请求）
- 定期清理旧日志（保留 90 天）

## 需求验证

本实现满足以下需求：

- **需求 6.2**: 支持用户角色分配和管理
- **需求 6.5**: 支持权限的动态调整，无需重启服务

### 验证的正确性属性

- **属性 12**: 用户角色分配 - 系统正确分配和持久化角色
- **属性 13**: 权限检查正确性 - 根据角色正确判断权限
- **属性 14**: 权限不足错误提示 - 返回明确的错误信息
- **属性 15**: 权限动态更新 - 更新后立即生效
- **属性 17**: 关键操作日志记录 - 记录详细的操作日志

## 未来改进

1. **批量操作**: 支持批量更新角色或删除用户
2. **用户搜索**: 支持按用户名或邮箱搜索
3. **用户统计**: 提供用户统计信息（按角色、状态等）
4. **导出功能**: 支持导出用户列表为 CSV
5. **用户恢复**: 支持恢复已删除（停用）的用户
6. **密码重置**: 管理员可以重置用户密码

## 相关文档

- [认证服务文档](../services/AUTHENTICATION_SERVICE_README.md)
- [授权服务文档](../services/AUTHORIZATION_SERVICE_README.md)
- [审计日志服务文档](../services/AUDIT_LOG_SERVICE_README.md)
- [认证中间件文档](../middleware/AUTH_MIDDLEWARE_README.md)
- [安全部署需求](../../.kiro/specs/secure-remote-deployment/requirements.md)
- [安全部署设计](../../.kiro/specs/secure-remote-deployment/design.md)
