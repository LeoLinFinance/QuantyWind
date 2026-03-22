# 认证中间件文档

## 概述

认证中间件模块提供了完整的身份验证、授权和请求限流功能，用于保护 FastAPI 应用的 API 端点。

## 功能特性

### 1. JWT 令牌验证

- 自动从请求头中提取和验证 JWT 令牌
- 支持 Bearer 认证方案
- 验证令牌有效性、过期时间和签名
- 检查令牌黑名单（已撤销的令牌）

### 2. 权限检查

- 基于角色的访问控制（RBAC）
- 支持三种角色：viewer（查看者）、user（用户）、admin（管理员）
- 细粒度的资源和操作权限控制
- 动态权限更新，无需重启服务

### 3. 请求限流

- 基于用户的请求限流
- 使用滑动窗口算法
- 默认限制：每用户每分钟 100 请求
- 支持自定义限流配置
- 独立的用户限流计数

## 使用方法

### 1. 获取当前用户

使用 `get_current_user` 依赖项自动验证令牌并获取用户信息：

```python
from fastapi import APIRouter, Depends
from backend.middleware.auth_middleware import get_current_user
from backend.services.authentication_service import TokenPayload

router = APIRouter()

@router.get("/api/profile")
async def get_profile(current_user: TokenPayload = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role
    }
```

### 2. 权限检查

使用 `require_permission` 装饰器保护需要特定权限的端点：

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.middleware.auth_middleware import require_permission, get_current_user
from backend.services.authentication_service import TokenPayload
from backend.database.config import get_db

router = APIRouter()

@router.delete("/api/portfolio/{id}")
@require_permission("portfolio", "delete")
async def delete_portfolio(
    id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 删除投资组合
    return {"message": "Portfolio deleted"}
```

### 3. 请求限流

#### 方法 A：使用默认限流器（推荐）

```python
from fastapi import APIRouter, Depends
from backend.middleware.auth_middleware import get_current_user, apply_rate_limit
from backend.services.authentication_service import TokenPayload

router = APIRouter()

@router.get("/api/data")
async def get_data(
    current_user: TokenPayload = Depends(get_current_user),
    _: None = Depends(apply_rate_limit)  # 应用默认限流（100 请求/分钟）
):
    return {"data": "..."}
```

#### 方法 B：使用自定义限流器

```python
from fastapi import APIRouter, Depends
from backend.middleware.auth_middleware import get_current_user, create_rate_limiter
from backend.services.authentication_service import TokenPayload

# 创建更严格的限流器：每分钟 10 请求
strict_rate_limit = create_rate_limiter(max_requests=10, window_seconds=60)

router = APIRouter()

@router.post("/api/expensive-operation")
async def expensive_operation(
    current_user: TokenPayload = Depends(get_current_user),
    _: None = Depends(strict_rate_limit)
):
    return {"result": "..."}
```

#### 方法 C：手动调用限流器

```python
from fastapi import APIRouter, Depends
from backend.middleware.auth_middleware import get_current_user, RateLimiter
from backend.services.authentication_service import TokenPayload

router = APIRouter()
rate_limiter = RateLimiter(max_requests=50, window_seconds=60)

@router.get("/api/custom")
async def custom_endpoint(current_user: TokenPayload = Depends(get_current_user)):
    # 手动检查限流
    rate_limiter.check_rate_limit(current_user.user_id)
    
    # 获取剩余配额
    quota = rate_limiter.get_remaining_requests(current_user.user_id)
    
    return {
        "data": "...",
        "rate_limit": quota
    }
```

### 4. 组合使用

同时使用认证、权限检查和限流：

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.middleware.auth_middleware import (
    get_current_user,
    require_permission,
    apply_rate_limit
)
from backend.services.authentication_service import TokenPayload
from backend.database.config import get_db

router = APIRouter()

@router.post("/api/admin/users")
@require_permission("user_management", "write")
async def create_user(
    user_data: dict,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: None = Depends(apply_rate_limit)
):
    # 创建用户（仅管理员可访问，且受限流保护）
    return {"message": "User created"}
```

## 角色权限矩阵

### Viewer（查看者）

只读权限，可查看数据但不能修改：

- portfolio: read
- market_data: read
- risk_analysis: read
- sentiment_map: read
- ai_signals: read
- expert_forum: read
- news: read

### User（用户）

标准用户权限，可使用所有功能：

- portfolio: read, write
- market_data: read, write
- risk_analysis: read, write
- sentiment_map: read, write
- ai_signals: read, write
- expert_forum: read, write
- news: read, write
- profile: read, write

### Admin（管理员）

完全权限，可管理用户和系统配置：

- 所有 User 权限
- portfolio: read, write, delete
- market_data: read, write, delete
- user_management: read, write, delete
- system_config: read, write, delete
- audit_logs: read
- license_management: read, write

## 错误处理

### 认证错误（401 Unauthorized）

当令牌无效、过期或缺失时返回：

```json
{
  "detail": "令牌已过期，请重新登录"
}
```

### 权限不足错误（403 Forbidden）

当用户没有足够权限时返回：

```json
{
  "detail": "您没有权限执行此操作。需要 portfolio:delete 权限"
}
```

### 请求限流错误（429 Too Many Requests）

当超过请求限制时返回：

```json
{
  "detail": "请求过于频繁。限制：100 请求/60 秒"
}
```

响应头包含：
- `Retry-After: 60` - 建议等待的秒数

## 配置

### 限流配置

默认限流配置：
- 最大请求数：100
- 时间窗口：60 秒（1 分钟）

可以通过创建自定义 `RateLimiter` 实例来修改：

```python
custom_limiter = RateLimiter(
    max_requests=200,      # 每个时间窗口的最大请求数
    window_seconds=120     # 时间窗口大小（秒）
)
```

### JWT 配置

JWT 配置在 `AuthenticationService` 中管理：
- 访问令牌有效期：30 分钟
- 刷新令牌有效期：7 天
- 签名算法：HS256

## 安全最佳实践

1. **始终使用 HTTPS**：确保所有 API 请求通过 HTTPS 传输
2. **定期轮换密钥**：定期更新 JWT 密钥
3. **最小权限原则**：为用户分配最小必要权限
4. **监控异常活动**：监控失败的认证尝试和权限检查
5. **限流保护**：为所有公开端点应用限流
6. **令牌撤销**：用户登出时立即撤销令牌

## 测试

运行测试：

```bash
pytest tests/test_auth_middleware_simple.py -v
```

测试覆盖：
- JWT 令牌验证
- 权限检查（所有角色）
- 请求限流（正常、超限、重置）
- 多用户独立限流

## 集成示例

完整的路由保护示例：

```python
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.orm import Session
from backend.middleware.auth_middleware import (
    get_current_user,
    require_permission,
    apply_rate_limit
)
from backend.services.authentication_service import TokenPayload
from backend.database.config import get_db

app = FastAPI()
router = APIRouter(prefix="/api", tags=["protected"])

# 公开端点（无需认证）
@router.get("/public/health")
async def health_check():
    return {"status": "ok"}

# 需要认证的端点
@router.get("/protected/profile")
async def get_profile(current_user: TokenPayload = Depends(get_current_user)):
    return {"user_id": current_user.user_id}

# 需要特定权限的端点
@router.post("/protected/portfolio")
@require_permission("portfolio", "write")
async def create_portfolio(
    data: dict,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {"message": "Portfolio created"}

# 受限流保护的端点
@router.get("/protected/data")
async def get_data(
    current_user: TokenPayload = Depends(get_current_user),
    _: None = Depends(apply_rate_limit)
):
    return {"data": "..."}

# 组合保护：认证 + 权限 + 限流
@router.delete("/protected/admin/user/{user_id}")
@require_permission("user_management", "delete")
async def delete_user(
    user_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: None = Depends(apply_rate_limit)
):
    return {"message": f"User {user_id} deleted"}

app.include_router(router)
```

## 故障排查

### 问题：令牌验证失败

**原因**：
- 令牌已过期
- 令牌已被撤销
- JWT 密钥不匹配

**解决方案**：
1. 检查令牌是否在有效期内
2. 确认令牌未在黑名单中
3. 验证 JWT_SECRET_KEY 环境变量

### 问题：权限检查失败

**原因**：
- 用户角色不正确
- 权限矩阵配置错误
- 用户账户被锁定或未激活

**解决方案**：
1. 检查用户角色：`user.role`
2. 验证权限矩阵配置
3. 确认用户账户状态

### 问题：限流过于严格

**原因**：
- 限流配置过于严格
- 多个请求同时发送

**解决方案**：
1. 调整限流参数（增加 `max_requests` 或 `window_seconds`）
2. 实现请求队列或批处理
3. 为不同端点使用不同的限流配置

## 相关文档

- [认证服务文档](../services/AUTHENTICATION_SERVICE_README.md)
- [授权服务文档](../services/AUTHORIZATION_SERVICE_README.md)
- [会话服务文档](../services/SESSION_SERVICE_README.md)
- [安全部署需求](../../.kiro/specs/secure-remote-deployment/requirements.md)
- [安全部署设计](../../.kiro/specs/secure-remote-deployment/design.md)
