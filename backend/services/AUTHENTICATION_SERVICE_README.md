# 身份验证服务 (Authentication Service)

## 概述

身份验证服务提供完整的用户认证和授权管理功能，包括用户注册、登录、令牌管理和账户安全机制。

## 功能特性

### 1. 用户注册
- ✅ 密码强度验证（8-128字符，包含大小写字母、数字和特殊字符）
- ✅ 用户名和邮箱唯一性检查
- ✅ bcrypt 密码哈希（工作因子 12）
- ✅ 角色分配（viewer, user, admin）

### 2. 用户登录
- ✅ 凭证验证
- ✅ JWT 令牌生成（访问令牌 + 刷新令牌）
- ✅ 访问令牌有效期：30 分钟
- ✅ 刷新令牌有效期：7 天
- ✅ 最后登录时间记录

### 3. 令牌管理
- ✅ JWT 令牌验证（HS256 算法）
- ✅ 令牌刷新机制
- ✅ 令牌撤销（Redis 黑名单）
- ✅ 令牌类型区分（access/refresh）

### 4. 账户安全
- ✅ 账户锁定机制（5 次失败后锁定 15 分钟）
- ✅ 失败登录计数
- ✅ 自动解锁（基于 Redis TTL）
- ✅ 账户激活状态检查

## 使用示例

### 注册用户

```python
from backend.services.authentication_service import get_authentication_service
from backend.database.config import get_db

auth_service = get_authentication_service()
db = next(get_db())

try:
    user = auth_service.register_user(
        username="john_doe",
        password="SecurePass123!",
        email="john@example.com",
        role="user",
        db=db
    )
    print(f"用户注册成功: {user.username}")
except UserAlreadyExistsError as e:
    print(f"注册失败: {e}")
except WeakPasswordError as e:
    print(f"密码强度不足: {e}")
```

### 用户登录

```python
try:
    auth_token = auth_service.authenticate(
        username="john_doe",
        password="SecurePass123!",
        db=db
    )
    print(f"登录成功!")
    print(f"访问令牌: {auth_token.access_token}")
    print(f"刷新令牌: {auth_token.refresh_token}")
    print(f"有效期: {auth_token.expires_in} 秒")
except InvalidCredentialsError as e:
    print(f"登录失败: {e}")
except AccountLockedError as e:
    print(f"账户被锁定: {e}")
```

### 验证令牌

```python
try:
    payload = auth_service.verify_token(access_token)
    print(f"用户 ID: {payload.user_id}")
    print(f"用户名: {payload.username}")
    print(f"角色: {payload.role}")
except TokenExpiredError:
    print("令牌已过期")
except InvalidTokenError:
    print("令牌无效")
```

### 刷新令牌

```python
try:
    new_auth_token = auth_service.refresh_token(refresh_token, db)
    print(f"令牌刷新成功!")
    print(f"新访问令牌: {new_auth_token.access_token}")
except InvalidTokenError as e:
    print(f"刷新失败: {e}")
```

### 撤销令牌

```python
success = auth_service.revoke_token(access_token)
if success:
    print("令牌已撤销")
```

## 数据模型

### AuthToken
```python
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 1800
}
```

### TokenPayload
```python
{
    "user_id": "uuid",
    "username": "john_doe",
    "role": "user",
    "exp": 1234567890.0,
    "token_type": "access"
}
```

## 环境变量

```bash
# JWT 密钥（生产环境必须设置）
JWT_SECRET_KEY=your_secret_key_here

# 环境标识
ENVIRONMENT=production

# Redis 连接（用于令牌黑名单和账户锁定）
REDIS_URL=redis://:password@localhost:6379/0
```

## 安全特性

1. **密码安全**
   - bcrypt 哈希（工作因子 12）
   - 密码强度验证
   - 72 字节长度限制（bcrypt 限制）

2. **令牌安全**
   - JWT 签名验证
   - 令牌过期检查
   - 黑名单机制（撤销）
   - 令牌类型验证

3. **账户保护**
   - 失败登录限制
   - 自动账户锁定
   - 基于时间的解锁
   - 账户激活状态检查

4. **错误处理**
   - 统一的错误消息（不泄露敏感信息）
   - 详细的异常类型
   - 安全的失败响应

## 测试

运行测试套件：

```bash
python3 -m pytest tests/test_authentication_service.py -v
```

测试覆盖：
- ✅ 密码强度验证（6 个测试）
- ✅ 用户注册（5 个测试）
- ✅ 用户登录（4 个测试）
- ✅ 账户锁定（2 个测试）
- ✅ 令牌验证（3 个测试）
- ✅ 令牌刷新（3 个测试）
- ✅ 令牌撤销（2 个测试）
- ✅ 边缘情况（4 个测试）

**总计：29 个测试，全部通过 ✅**

## 依赖项

- `pyjwt` - JWT 令牌生成和验证
- `bcrypt` - 密码哈希
- `redis` - 令牌黑名单和账户锁定
- `sqlalchemy` - 数据库 ORM
- `cryptography` - 加密服务依赖

## 性能考虑

1. **Redis 缓存**
   - 令牌黑名单存储在 Redis（快速查询）
   - 账户锁定状态存储在 Redis（自动过期）
   - TTL 自动清理过期数据

2. **密码哈希**
   - bcrypt 工作因子 12（平衡安全性和性能）
   - 异步处理建议（避免阻塞）

3. **数据库查询**
   - 用户名和邮箱字段已索引
   - 最小化数据库往返

## 已知限制

1. **bcrypt 密码长度**
   - 最大 72 字节（超出部分被截断）
   - 建议在应用层限制为 128 字符

2. **令牌撤销**
   - 需要 Redis 支持
   - 黑名单在令牌过期后自动清理

3. **账户锁定**
   - 基于 Redis TTL（服务器重启不影响）
   - 锁定时间固定为 15 分钟

## 未来改进

- [ ] 支持多因素认证（MFA）
- [ ] 支持 OAuth 2.0 第三方登录
- [ ] 支持密码重置功能
- [ ] 支持邮箱验证
- [ ] 支持设备指纹识别
- [ ] 支持地理位置异常检测

## 相关文档

- [需求文档](../../.kiro/specs/secure-remote-deployment/requirements.md)
- [设计文档](../../.kiro/specs/secure-remote-deployment/design.md)
- [任务列表](../../.kiro/specs/secure-remote-deployment/tasks.md)
- [加密服务](./ENCRYPTION_SERVICE_README.md)

## 维护者

- 实现日期：2025-01-15
- 需求：2.1, 2.2, 2.3, 2.4
- 测试状态：✅ 全部通过
