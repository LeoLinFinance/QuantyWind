# 审计日志服务 (Audit Log Service)

## 概述

审计日志服务用于记录所有安全相关事件，包括身份验证、授权检查和系统操作。该服务提供完整的日志记录、查询和管理功能，支持安全审计和问题追溯。

## 功能特性

- ✅ 身份验证事件日志记录（登录、登出、注册、令牌刷新）
- ✅ 授权检查日志记录（权限验证、访问控制）
- ✅ 安全事件日志记录（入侵尝试、账户锁定、会话劫持）
- ✅ 灵活的日志查询功能（支持多种过滤条件和分页）
- ✅ 失败登录追踪（支持按用户和 IP 地址统计）
- ✅ 日志自动清理和归档（默认保留 90 天）
- ✅ 统计分析功能（事件类型、严重程度统计）

## 快速开始

### 1. 初始化服务

```python
from sqlalchemy.orm import Session
from backend.services.audit_log_service import AuditLogService

# 使用数据库会话创建服务实例
audit_service = AuditLogService(db)
```

### 2. 记录身份验证事件

```python
# 记录成功登录
audit_service.log_authentication(
    user_id="user_123",
    action="login",
    success=True,
    ip_address="192.168.1.100",
    details={
        "user_agent": "Mozilla/5.0...",
        "session_id": "sess_xyz789"
    }
)

# 记录失败登录
audit_service.log_authentication(
    user_id="user_123",
    action="login",
    success=False,
    ip_address="192.168.1.100",
    details={
        "failure_reason": "invalid_password"
    }
)

# 记录用户登出
audit_service.log_authentication(
    user_id="user_123",
    action="logout",
    success=True,
    ip_address="192.168.1.100"
)
```

### 3. 记录授权检查事件

```python
# 记录授权成功
audit_service.log_authorization(
    user_id="user_123",
    resource="portfolio",
    action="read",
    granted=True
)

# 记录授权拒绝
audit_service.log_authorization(
    user_id="user_123",
    resource="user_management",
    action="write",
    granted=False,
    reason="insufficient_permissions"
)
```

### 4. 记录安全事件

```python
# 记录账户锁定
audit_service.log_security_event(
    event_type="account_locked",
    severity="high",
    description="Account locked due to 5 failed login attempts",
    metadata={
        "failed_attempts": 5,
        "lock_duration": "15 minutes"
    },
    user_id="user_123",
    ip_address="192.168.1.100"
)

# 记录入侵尝试
audit_service.log_security_event(
    event_type="intrusion_attempt",
    severity="critical",
    description="SQL injection attempt detected",
    metadata={
        "attack_type": "sql_injection",
        "payload": "' OR '1'='1"
    },
    ip_address="192.168.1.200"
)
```

### 5. 查询日志

```python
from datetime import datetime, timedelta

# 查询最近 24 小时的失败登录
failed_logins = audit_service.query_logs(
    filters={
        "event_type": "authentication",
        "success": False
    },
    start_time=datetime.now() - timedelta(days=1)
)

# 查询特定用户的活动
user_activity = audit_service.get_user_activity(
    user_id="user_123",
    start_time=datetime.now() - timedelta(days=7)
)

# 查询高危安全事件
security_events = audit_service.get_security_events(
    severity="high",
    start_time=datetime.now() - timedelta(hours=1)
)
```

### 6. 失败登录追踪

```python
# 获取用户最近 15 分钟的失败登录次数
failed_count = audit_service.get_failed_login_attempts(
    user_id="user_123"
)

# 获取 IP 地址的失败登录次数
failed_count = audit_service.get_failed_login_attempts(
    ip_address="192.168.1.100",
    time_window=timedelta(minutes=30)
)
```

### 7. 统计分析

```python
# 获取今天的统计信息
stats = audit_service.get_statistics(
    start_time=datetime.now().replace(hour=0, minute=0, second=0)
)

print(f"总事件数: {stats['total_events']}")
print(f"失败认证: {stats['failed_authentications']}")
print(f"拒绝授权: {stats['denied_authorizations']}")
print(f"按事件类型: {stats['by_event_type']}")
print(f"按严重程度: {stats['by_severity']}")
```

### 8. 日志清理

```python
# 删除 90 天前的日志
deleted_count = audit_service.cleanup_old_logs(retention_days=90)
print(f"已删除 {deleted_count} 条旧日志")
```

## API 参考

### log_authentication()

记录身份验证事件。

**参数：**
- `user_id` (str, optional): 用户 ID
- `action` (str): 操作类型（login, logout, register, token_refresh）
- `success` (bool): 是否成功
- `ip_address` (str): IP 地址
- `details` (dict, optional): 额外详情

**返回：** `AuditLog` 对象

### log_authorization()

记录授权检查事件。

**参数：**
- `user_id` (str): 用户 ID
- `resource` (str): 资源标识符
- `action` (str): 操作类型（read, write, delete）
- `granted` (bool): 是否授权
- `reason` (str, optional): 原因

**返回：** `AuditLog` 对象

### log_security_event()

记录安全事件。

**参数：**
- `event_type` (str): 事件类型
- `severity` (str): 严重程度（low, medium, high, critical）
- `description` (str): 事件描述
- `metadata` (dict, optional): 元数据
- `user_id` (str, optional): 相关用户 ID
- `ip_address` (str, optional): 相关 IP 地址

**返回：** `AuditLog` 对象

### query_logs()

查询审计日志。

**参数：**
- `filters` (dict, optional): 过滤条件
  - `event_type`: 事件类型
  - `user_id`: 用户 ID
  - `action`: 操作类型
  - `success`: 是否成功
  - `severity`: 严重程度
  - `ip_address`: IP 地址
- `start_time` (datetime, optional): 开始时间
- `end_time` (datetime, optional): 结束时间
- `limit` (int): 返回结果数量限制（默认 100）
- `offset` (int): 偏移量（用于分页）

**返回：** `List[AuditLog]`

### get_failed_login_attempts()

获取失败登录次数。

**参数：**
- `user_id` (str, optional): 用户 ID
- `ip_address` (str, optional): IP 地址
- `time_window` (timedelta): 时间窗口（默认 15 分钟）

**返回：** `int`

### get_security_events()

获取安全事件日志。

**参数：**
- `severity` (str, optional): 严重程度过滤
- `start_time` (datetime, optional): 开始时间
- `limit` (int): 返回结果数量限制（默认 50）

**返回：** `List[AuditLog]`

### get_user_activity()

获取用户活动日志。

**参数：**
- `user_id` (str): 用户 ID
- `start_time` (datetime, optional): 开始时间
- `end_time` (datetime, optional): 结束时间
- `limit` (int): 返回结果数量限制（默认 100）

**返回：** `List[AuditLog]`

### cleanup_old_logs()

清理旧日志。

**参数：**
- `retention_days` (int): 保留天数（默认 90）

**返回：** `int` - 删除的日志数量

### get_statistics()

获取审计日志统计信息。

**参数：**
- `start_time` (datetime, optional): 开始时间
- `end_time` (datetime, optional): 结束时间

**返回：** `dict` - 统计信息字典

## 日志格式

审计日志包含以下字段：

```python
{
    "id": "uuid",                    # 日志 ID
    "event_type": "authentication",  # 事件类型
    "action": "login",               # 操作
    "user_id": "user_123",           # 用户 ID
    "resource": "portfolio",         # 资源（可选）
    "ip_address": "192.168.1.100",   # IP 地址
    "success": true,                 # 是否成功
    "severity": "info",              # 严重程度
    "details": {...},                # 详细信息
    "timestamp": "2024-01-15T10:30:45.123Z"  # 时间戳
}
```

## 严重程度级别

- **low**: 低危事件（正常操作）
- **medium**: 中危事件（失败的认证、拒绝的授权）
- **high**: 高危事件（账户锁定、会话异常）
- **critical**: 严重事件（入侵尝试、系统攻击）

## 事件类型

### authentication（身份验证）
- `login`: 用户登录
- `logout`: 用户登出
- `register`: 用户注册
- `token_refresh`: 令牌刷新

### authorization（授权）
- `read_*`: 读取操作
- `write_*`: 写入操作
- `delete_*`: 删除操作

### security_event（安全事件）
- `account_locked`: 账户锁定
- `intrusion_attempt`: 入侵尝试
- `session_hijack`: 会话劫持
- `suspicious_activity`: 可疑活动

## 最佳实践

### 1. 记录所有关键操作

```python
# 在认证服务中
def login(username, password):
    try:
        user = authenticate(username, password)
        audit_service.log_authentication(
            user_id=user.id,
            action="login",
            success=True,
            ip_address=request.remote_addr
        )
        return user
    except AuthenticationError as e:
        audit_service.log_authentication(
            user_id=username,  # 使用用户名，因为认证失败
            action="login",
            success=False,
            ip_address=request.remote_addr,
            details={"failure_reason": str(e)}
        )
        raise
```

### 2. 实施账户锁定

```python
def check_account_lockout(user_id, ip_address):
    # 检查失败登录次数
    failed_attempts = audit_service.get_failed_login_attempts(
        user_id=user_id,
        time_window=timedelta(minutes=15)
    )
    
    if failed_attempts >= 5:
        # 锁定账户
        lock_account(user_id)
        
        # 记录安全事件
        audit_service.log_security_event(
            event_type="account_locked",
            severity="high",
            description=f"Account locked due to {failed_attempts} failed login attempts",
            metadata={"failed_attempts": failed_attempts},
            user_id=user_id,
            ip_address=ip_address
        )
        
        raise AccountLockedError("Account has been locked")
```

### 3. 监控安全事件

```python
def monitor_security_events():
    # 获取最近 1 小时的高危事件
    events = audit_service.get_security_events(
        severity="high",
        start_time=datetime.now() - timedelta(hours=1)
    )
    
    if len(events) > 10:
        # 触发告警
        send_alert(f"检测到 {len(events)} 个高危安全事件")
```

### 4. 定期清理日志

```python
# 在定时任务中执行
def cleanup_audit_logs():
    deleted_count = audit_service.cleanup_old_logs(retention_days=90)
    logger.info(f"Cleaned up {deleted_count} old audit logs")
```

### 5. 生成安全报告

```python
def generate_security_report(start_date, end_date):
    stats = audit_service.get_statistics(
        start_time=start_date,
        end_time=end_date
    )
    
    report = {
        "period": f"{start_date} to {end_date}",
        "total_events": stats["total_events"],
        "failed_authentications": stats["failed_authentications"],
        "denied_authorizations": stats["denied_authorizations"],
        "security_events": stats["by_event_type"]["security_event"],
        "critical_events": stats["by_severity"]["critical"]
    }
    
    return report
```

## 性能优化

### 1. 使用索引

数据库表已经创建了以下索引以优化查询性能：
- `event_type` - 按事件类型查询
- `user_id` - 按用户查询
- `timestamp` - 按时间范围查询
- 复合索引：`(user_id, timestamp)`, `(event_type, timestamp)`, `(severity, timestamp)`

### 2. 分页查询

对于大量日志，使用分页查询：

```python
# 分页获取日志
page_size = 100
page = 0

while True:
    logs = audit_service.query_logs(
        limit=page_size,
        offset=page * page_size
    )
    
    if not logs:
        break
    
    process_logs(logs)
    page += 1
```

### 3. 异步日志记录

对于高并发场景，考虑使用异步日志记录：

```python
import asyncio

async def log_async(audit_service, *args, **kwargs):
    await asyncio.to_thread(
        audit_service.log_authentication,
        *args,
        **kwargs
    )
```

## 故障排查

### 问题：日志查询很慢

**解决方案：**
1. 检查是否使用了索引字段进行过滤
2. 缩小时间范围
3. 使用分页查询
4. 考虑定期归档旧日志

### 问题：磁盘空间不足

**解决方案：**
1. 调整日志保留期限
2. 定期执行 `cleanup_old_logs()`
3. 考虑将旧日志归档到外部存储

### 问题：时间戳不一致

**解决方案：**
- 服务使用 UTC 时间，确保所有系统时钟同步
- 在查询时使用 UTC 时间进行比较

## 安全考虑

1. **访问控制**: 只有管理员应该能够查询和删除审计日志
2. **数据完整性**: 审计日志不应该被修改，只能创建和删除
3. **敏感信息**: 避免在日志中记录密码、令牌等敏感信息
4. **日志保护**: 定期备份审计日志，防止数据丢失

## 相关文档

- [身份验证服务](./AUTHENTICATION_SERVICE_README.md)
- [授权服务](./AUTHORIZATION_SERVICE_README.md)
- [会话管理服务](./SESSION_SERVICE_README.md)
- [设计文档](../../.kiro/specs/secure-remote-deployment/design.md)

## 测试

运行单元测试：

```bash
python3 -m pytest tests/test_audit_log_service.py -v
```

## 许可证

本服务是"量数风行"安全远程访问部署系统的一部分。
