# 会话管理服务 (Session Service)

## 概述

会话管理服务负责管理用户会话的完整生命周期，包括创建、验证、更新和终止会话。该服务使用 Redis 作为会话存储，提供高性能的会话管理能力。

## 功能特性

- ✅ **会话创建**：为用户创建新的会话，生成唯一的会话 ID 和令牌
- ✅ **会话验证**：验证会话的有效性，包括过期检查和 IP 地址验证
- ✅ **会话活动更新**：更新会话的最后活动时间，延长会话有效期
- ✅ **会话终止**：终止单个或所有用户会话
- ✅ **多会话管理**：支持单用户多会话，最多 3 个并发会话
- ✅ **安全检查**：检测 IP 地址变化，防止会话劫持

## 核心配置

```python
# 会话超时时间（分钟）
SESSION_TIMEOUT_MINUTES = 30

# 每个用户最大并发会话数
MAX_SESSIONS_PER_USER = 3
```

## 使用方法

### 1. 获取服务实例

```python
from backend.services.session_service import get_session_service

session_service = get_session_service()
```

### 2. 创建会话

```python
# 用户登录成功后创建会话
session = session_service.create_session(
    user_id="user_123",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)

print(f"会话 ID: {session.id}")
print(f"会话令牌: {session.token}")
print(f"过期时间: {session.expires_at}")
```

### 3. 验证会话

```python
from backend.services.session_service import SessionExpiredError, SessionAnomalyError

try:
    # 验证会话是否有效
    is_valid = session_service.validate_session(
        session_id=session.id,
        ip_address="192.168.1.100"
    )
    print("会话有效")
except SessionExpiredError as e:
    print(f"会话已过期: {e}")
except SessionAnomalyError as e:
    print(f"会话异常（IP 地址变化）: {e}")
```

### 4. 更新会话活动

```python
# 用户执行操作时更新会话活动时间
success = session_service.update_activity(session.id)
if success:
    print("会话活动时间已更新")
```

### 5. 获取用户的所有活动会话

```python
# 获取用户的所有活动会话
active_sessions = session_service.get_active_sessions(user_id="user_123")

for session in active_sessions:
    print(f"会话 ID: {session.id}")
    print(f"创建时间: {session.created_at}")
    print(f"最后活动: {session.last_activity}")
    print(f"IP 地址: {session.ip_address}")
    print("---")
```

### 6. 终止会话

```python
# 用户登出时终止会话
success = session_service.terminate_session(session.id)
if success:
    print("会话已终止")

# 或者终止用户的所有会话（例如：密码修改后）
count = session_service.terminate_all_user_sessions(user_id="user_123")
print(f"已终止 {count} 个会话")
```

## 会话对象结构

```python
class Session:
    id: str                # 会话唯一标识符（UUID）
    user_id: str           # 用户 ID
    token: str             # 会话令牌（UUID）
    ip_address: str        # 客户端 IP 地址
    user_agent: str        # 客户端 User-Agent
    created_at: datetime   # 创建时间
    last_activity: datetime # 最后活动时间
    expires_at: datetime   # 过期时间
    is_active: bool        # 是否活动
```

## 异常类型

### SessionError
会话相关错误的基类。

### SessionExpiredError
会话已过期错误。当会话不存在、已过期或非活动时抛出。

```python
try:
    session_service.validate_session(session_id, ip_address)
except SessionExpiredError:
    # 重定向到登录页面
    return redirect("/login")
```

### SessionAnomalyError
会话异常错误。当检测到 IP 地址变化等异常情况时抛出。

```python
try:
    session_service.validate_session(session_id, ip_address)
except SessionAnomalyError:
    # 记录安全事件并要求重新验证
    audit_log_service.log_security_event(
        event_type="session_anomaly",
        severity="high",
        description="IP address mismatch detected"
    )
    return redirect("/login")
```

### MaxSessionsExceededError
超过最大会话数错误。当用户尝试创建超过限制的会话时抛出（当前实现会自动删除最旧的会话）。

## 安全特性

### 1. IP 地址验证
会话创建时记录客户端 IP 地址，每次验证时检查 IP 是否一致。如果 IP 地址发生变化，会话将被终止并抛出 `SessionAnomalyError`。

```python
# 会话创建时记录 IP
session = session_service.create_session(
    user_id="user_123",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0"
)

# 验证时检查 IP
try:
    session_service.validate_session(session.id, "192.168.1.200")  # 不同的 IP
except SessionAnomalyError:
    # IP 地址变化，会话已被终止
    pass
```

### 2. 会话超时
会话在 30 分钟无活动后自动过期。每次更新活动时间会延长过期时间。

```python
# 每次用户操作时更新活动时间
@app.middleware("http")
async def update_session_activity(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    if session_id:
        session_service.update_activity(session_id)
    response = await call_next(request)
    return response
```

### 3. 多会话限制
每个用户最多可以有 3 个并发会话。当创建第 4 个会话时，最旧的会话将被自动删除。

```python
# 创建多个会话
for i in range(5):
    session = session_service.create_session(
        user_id="user_123",
        ip_address=f"192.168.1.{i}",
        user_agent="Mozilla/5.0"
    )

# 只有最新的 3 个会话是活动的
active_sessions = session_service.get_active_sessions("user_123")
assert len(active_sessions) == 3
```

## 与其他服务集成

### 与身份验证服务集成

```python
from backend.services.authentication_service import get_authentication_service
from backend.services.session_service import get_session_service

auth_service = get_authentication_service()
session_service = get_session_service()

# 用户登录
def login(username: str, password: str, ip_address: str, user_agent: str):
    # 1. 验证用户凭证
    auth_token = auth_service.authenticate(username, password, db)
    
    # 2. 创建会话
    session = session_service.create_session(
        user_id=auth_token.user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {
        "access_token": auth_token.access_token,
        "session_id": session.id,
        "session_token": session.token
    }
```

### 与审计日志服务集成

```python
from backend.services.audit_log_service import get_audit_log_service

audit_service = get_audit_log_service()

# 记录会话创建
session = session_service.create_session(user_id, ip_address, user_agent)
audit_service.log_authentication(
    user_id=user_id,
    action="session_created",
    success=True,
    ip_address=ip_address,
    details={"session_id": session.id}
)

# 记录会话异常
try:
    session_service.validate_session(session_id, ip_address)
except SessionAnomalyError as e:
    audit_service.log_security_event(
        event_type="session_anomaly",
        severity="high",
        description=str(e),
        metadata={"session_id": session_id, "ip_address": ip_address}
    )
```

## FastAPI 中间件示例

```python
from fastapi import FastAPI, Request, HTTPException
from backend.services.session_service import (
    get_session_service,
    SessionExpiredError,
    SessionAnomalyError
)

app = FastAPI()
session_service = get_session_service()

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # 跳过公开路由
    if request.url.path in ["/login", "/register", "/health"]:
        return await call_next(request)
    
    # 获取会话 ID
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="未提供会话")
    
    # 验证会话
    try:
        client_ip = request.client.host
        session_service.validate_session(session_id, client_ip)
        
        # 更新活动时间
        session_service.update_activity(session_id)
        
        # 将会话信息添加到请求状态
        session = session_service.get_session(session_id)
        request.state.session = session
        request.state.user_id = session.user_id
        
    except SessionExpiredError:
        raise HTTPException(status_code=401, detail="会话已过期")
    except SessionAnomalyError:
        raise HTTPException(status_code=401, detail="会话异常，请重新登录")
    
    response = await call_next(request)
    return response
```

## Redis 数据结构

### 会话数据
```
键: session:{session_id}
值: JSON 字符串
TTL: 1800 秒（30 分钟）

示例:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123",
  "token": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2024-01-15T10:30:45.123456",
  "last_activity": "2024-01-15T10:35:12.789012",
  "expires_at": "2024-01-15T11:00:45.123456",
  "is_active": true
}
```

### 用户会话列表
```
键: user_sessions:{user_id}
类型: Set
值: 会话 ID 列表

示例:
user_sessions:user_123 = {
  "550e8400-e29b-41d4-a716-446655440000",
  "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## 性能考虑

1. **Redis 连接池**：使用连接池管理 Redis 连接，避免频繁创建和销毁连接。

2. **批量操作**：获取用户所有会话时，使用 Redis 的 SMEMBERS 和 MGET 命令批量获取数据。

3. **过期清理**：利用 Redis 的 TTL 机制自动清理过期会话，无需手动清理。

4. **内存优化**：会话数据使用 JSON 序列化，压缩存储空间。

## 测试

运行单元测试：

```bash
python3 -m pytest tests/test_session_service.py -v
```

测试覆盖：
- ✅ 会话创建
- ✅ 会话验证
- ✅ 会话活动更新
- ✅ 会话终止
- ✅ 多会话管理
- ✅ 边缘情况处理
- ✅ 序列化和反序列化

## 验证需求

该服务实现了以下需求：

- **需求 8.1**：生成唯一的会话令牌
- **需求 8.2**：设置合理的超时时间（30 分钟）
- **需求 8.3**：验证令牌的有效性和完整性
- **需求 8.4**：检测会话异常（IP 地址变化）
- **需求 8.5**：登出时失效会话令牌

## 未来改进

1. **地理位置验证**：除了 IP 地址，还可以验证地理位置变化。
2. **设备指纹**：使用设备指纹技术增强会话安全性。
3. **会话迁移**：支持会话在不同设备间安全迁移。
4. **会话分析**：提供会话使用情况的统计和分析功能。
5. **自适应超时**：根据用户行为动态调整会话超时时间。

## 相关文档

- [身份验证服务](./AUTHENTICATION_SERVICE_README.md)
- [授权服务](./AUTHORIZATION_SERVICE_README.md)
- [审计日志服务](./AUDIT_LOG_SERVICE_README.md)
- [设计文档](../../.kiro/specs/secure-remote-deployment/design.md)
- [需求文档](../../.kiro/specs/secure-remote-deployment/requirements.md)
