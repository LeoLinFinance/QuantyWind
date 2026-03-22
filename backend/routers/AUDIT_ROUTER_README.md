# 审计日志路由 (Audit Log Router)

## 概述

审计日志路由提供了查询和分析系统审计日志的 API 端点。所有端点都需要管理员权限，确保只有授权人员才能访问敏感的审计信息。

## API 端点

### 1. GET /api/audit/logs

查询审计日志，支持多种过滤条件和分页。

**权限要求**: 管理员 (admin)

**查询参数**:
- `page` (int, 默认: 1): 页码
- `page_size` (int, 默认: 50, 最大: 200): 每页数量
- `event_type` (string, 可选): 事件类型 (authentication, authorization, security_event)
- `user_id` (string, 可选): 用户 ID
- `action` (string, 可选): 操作类型
- `success` (boolean, 可选): 是否成功
- `severity` (string, 可选): 严重程度 (low, medium, high, critical)
- `ip_address` (string, 可选): IP 地址
- `resource` (string, 可选): 资源
- `start_date` (string, 可选): 开始日期 (ISO 8601 格式或 YYYY-MM-DD)
- `end_date` (string, 可选): 结束日期 (ISO 8601 格式或 YYYY-MM-DD)

**响应示例**:
```json
{
  "logs": [
    {
      "id": "log_123",
      "timestamp": "2024-01-15T10:30:45.123Z",
      "event_type": "authentication",
      "action": "login",
      "user_id": "user_456",
      "ip_address": "192.168.1.100",
      "resource": null,
      "success": true,
      "severity": "info",
      "details": {
        "user_agent": "Mozilla/5.0...",
        "session_id": "sess_789"
      }
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 50,
  "filters": {
    "event_type": "authentication"
  }
}
```

**使用示例**:
```bash
# 查询所有审计日志
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/audit/logs

# 查询失败的登录尝试
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/logs?event_type=authentication&success=false"

# 查询特定用户的活动
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/logs?user_id=user_123"

# 查询特定日期范围的日志
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/logs?start_date=2024-01-01&end_date=2024-01-31"
```

### 2. GET /api/audit/security-events

查询安全事件，返回最近的安全相关事件。

**权限要求**: 管理员 (admin)

**查询参数**:
- `severity` (string, 可选): 严重程度过滤 (low, medium, high, critical)
- `hours` (int, 默认: 24, 最大: 720): 查询最近多少小时的事件
- `limit` (int, 默认: 100, 最大: 500): 返回结果数量限制

**响应示例**:
```json
{
  "events": [
    {
      "id": "event_123",
      "timestamp": "2024-01-15T10:30:45.123Z",
      "event_type": "security_event",
      "action": "account_locked",
      "user_id": "user_456",
      "ip_address": "192.168.1.100",
      "resource": null,
      "success": false,
      "severity": "high",
      "details": {
        "description": "Account locked due to 5 failed login attempts",
        "failed_attempts": 5,
        "lock_duration": "15 minutes"
      }
    }
  ],
  "total": 5,
  "severity_filter": "high"
}
```

**使用示例**:
```bash
# 查询所有安全事件
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/audit/security-events

# 查询高危安全事件
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/security-events?severity=high"

# 查询最近 1 小时的安全事件
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/security-events?hours=1"
```

## 功能特性

### 1. 权限控制
- 所有端点都需要管理员权限
- 使用 `require_admin` 辅助函数验证用户角色
- 未授权访问会返回 403 Forbidden

### 2. 过滤功能
支持多种过滤条件：
- 事件类型 (authentication, authorization, security_event)
- 用户 ID
- 操作类型
- 成功状态
- 严重程度
- IP 地址
- 资源
- 日期范围

### 3. 分页支持
- 可配置的页码和页面大小
- 返回总数以支持前端分页组件
- 默认每页 50 条记录，最大 200 条

### 4. 日期时间解析
- 支持 ISO 8601 格式 (2024-01-15T10:30:45)
- 支持简单日期格式 (2024-01-15)
- 自动处理时区和日期边界

### 5. 审计日志记录
- 所有审计日志访问本身也被记录
- 记录访问者身份和访问时间
- 便于追踪谁查看了审计日志

### 6. 错误处理
- 无效日期格式返回 400 Bad Request
- 无效严重程度返回 400 Bad Request
- 权限不足返回 403 Forbidden
- 清晰的错误消息

## 安全考虑

### 1. 访问控制
- 仅管理员可访问
- 每次请求都验证令牌和角色
- 记录所有访问尝试

### 2. 数据保护
- 不暴露敏感的内部实现细节
- 返回结构化的日志数据
- 支持按需过滤以减少数据传输

### 3. 审计追踪
- 记录谁访问了审计日志
- 记录访问时间和查询条件
- 便于安全审计和合规性检查

## 集成到主应用

在 `backend/main.py` 中注册路由：

```python
from backend.routers import audit

app.include_router(audit.router, tags=["audit"])
```

## 测试

测试文件位于 `tests/test_audit_router_standalone.py`，包含：

1. **权限测试**
   - 管理员可以访问
   - 普通用户被拒绝
   - 未认证用户被拒绝

2. **过滤测试**
   - 按事件类型过滤
   - 按用户 ID 过滤
   - 按成功状态过滤
   - 按严重程度过滤
   - 按 IP 地址过滤
   - 按资源过滤
   - 按操作类型过滤
   - 按日期范围过滤

3. **分页测试**
   - 第一页
   - 后续页面
   - 页面大小限制

4. **错误处理测试**
   - 无效日期格式
   - 无效严重程度
   - 空结果集

5. **数据结构测试**
   - 响应格式正确
   - 包含所有必需字段

运行测试（需要 Redis 运行）：
```bash
pytest tests/test_audit_router_standalone.py -v
```

## 依赖项

- `backend.services.audit_log_service`: 审计日志服务
- `backend.services.authorization_service`: 授权服务
- `backend.middleware.auth_middleware`: 认证中间件
- `backend.database.config`: 数据库配置

## 需求验证

此实现验证了以下需求：

- **需求 7.4**: 系统应当提供日志查询和分析功能
  - ✅ 提供了 `/api/audit/logs` 端点查询审计日志
  - ✅ 提供了 `/api/audit/security-events` 端点查询安全事件
  - ✅ 支持多种过滤条件和分页
  - ✅ 仅管理员可访问

## 使用场景

### 1. 安全审计
管理员可以查询所有安全相关事件，识别潜在的安全威胁：
```bash
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/security-events?severity=high"
```

### 2. 用户活动追踪
追踪特定用户的所有活动：
```bash
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/logs?user_id=user_123"
```

### 3. 失败登录分析
分析失败的登录尝试，识别暴力破解攻击：
```bash
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/logs?event_type=authentication&success=false"
```

### 4. 合规性报告
生成特定时间范围的审计报告：
```bash
curl -H "Authorization: Bearer <admin_token>" \
  "http://localhost:8000/api/audit/logs?start_date=2024-01-01&end_date=2024-01-31"
```

## 未来改进

1. **导出功能**: 支持导出审计日志为 CSV 或 JSON 文件
2. **实时告警**: 当检测到高危安全事件时发送实时告警
3. **可视化**: 提供审计日志的图表和统计信息
4. **高级搜索**: 支持全文搜索和复杂查询条件
5. **归档管理**: 自动归档旧日志到长期存储
