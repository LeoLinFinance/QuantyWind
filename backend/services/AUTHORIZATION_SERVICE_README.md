# 授权服务文档

## 概述

授权服务（`AuthorizationService`）实现了基于角色的访问控制（RBAC），为"量数风行"安全远程访问部署系统提供细粒度的权限管理。

## 功能特性

### 1. 基于角色的访问控制（RBAC）

系统定义了三种角色，每种角色具有不同的权限级别：

#### Viewer（查看者）
- **权限范围**：只读访问
- **可访问资源**：
  - portfolio（投资组合）- 读取
  - market_data（市场数据）- 读取
  - risk_analysis（风险分析）- 读取
  - sentiment_map（情绪地图）- 读取
  - ai_signals（AI 信号）- 读取
  - expert_forum（专家论坛）- 读取
  - news（新闻）- 读取

#### User（普通用户）
- **权限范围**：读写访问
- **可访问资源**：
  - 所有 Viewer 可访问的资源 + 写入权限
  - profile（个人资料）- 读写

#### Admin（管理员）
- **权限范围**：完全访问（读、写、删除）
- **可访问资源**：
  - 所有 User 可访问的资源 + 删除权限
  - user_management（用户管理）- 完全访问
  - system_config（系统配置）- 完全访问
  - audit_logs（审计日志）- 读取
  - license_management（许可证管理）- 读写

### 2. 权限检查

系统在执行任何操作前都会验证用户权限，确保：
- 用户账户处于激活状态
- 用户账户未被锁定
- 用户角色具有相应的资源访问权限
- 用户具有执行特定操作的权限

### 3. 动态角色管理

支持运行时动态更新用户角色，无需重启服务：
- 角色分配立即生效
- 权限变更实时反映在访问控制中
- 所有角色变更都会持久化到数据库

## 使用方法

### 初始化服务

```python
from sqlalchemy.orm import Session
from backend.services.authorization_service import AuthorizationService

# 创建授权服务实例
auth_service = AuthorizationService(db_session)
```

### 检查权限

```python
# 检查用户是否有权限读取投资组合
has_permission = auth_service.check_permission(
    user_id="user-123",
    resource="portfolio",
    action="read"
)

if has_permission:
    # 允许访问
    pass
else:
    # 拒绝访问
    raise PermissionError("权限不足")
```

### 获取用户权限

```python
# 获取用户的所有权限
permissions = auth_service.get_user_permissions(user_id="user-123")

for perm in permissions:
    print(f"资源: {perm.resource}, 操作: {perm.actions}")
```

### 分配角色

```python
# 为用户分配管理员角色
success = auth_service.assign_role(
    user_id="user-123",
    role="admin"
)

if success:
    print("角色分配成功")
```

### 更新角色

```python
# 更新用户角色
success = auth_service.update_role(
    user_id="user-123",
    new_role="user"
)
```

### 查询角色信息

```python
# 获取用户角色
role = auth_service.get_user_role(user_id="user-123")

# 检查是否具有特定角色
is_admin = auth_service.is_admin(user_id="user-123")

# 检查是否具有指定角色
has_role = auth_service.has_role(user_id="user-123", role="admin")
```

### 获取资源权限

```python
# 获取用户对特定资源的权限列表
permissions = auth_service.get_resource_permissions(
    user_id="user-123",
    resource="portfolio"
)
# 返回: ["read", "write"] 或 ["read", "write", "delete"]
```

### 静态方法

```python
# 获取所有可用资源列表
resources = AuthorizationService.get_all_resources()

# 获取完整的角色权限矩阵
matrix = AuthorizationService.get_role_permissions_matrix()
```

## API 集成示例

### FastAPI 依赖注入

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.services.authorization_service import AuthorizationService

def get_auth_service(db: Session = Depends(get_db)) -> AuthorizationService:
    """获取授权服务实例"""
    return AuthorizationService(db)

def require_permission(resource: str, action: str):
    """权限检查装饰器"""
    def permission_checker(
        current_user_id: str,
        auth_service: AuthorizationService = Depends(get_auth_service)
    ):
        if not auth_service.check_permission(current_user_id, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {resource} 的 {action} 权限"
            )
        return True
    return permission_checker
```

### 路由保护

```python
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/api/portfolio")
async def get_portfolio(
    _: bool = Depends(require_permission("portfolio", "read")),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取投资组合（需要读取权限）"""
    # 业务逻辑
    pass

@router.post("/api/portfolio")
async def create_portfolio(
    _: bool = Depends(require_permission("portfolio", "write")),
    current_user_id: str = Depends(get_current_user_id)
):
    """创建投资组合（需要写入权限）"""
    # 业务逻辑
    pass

@router.delete("/api/portfolio/{id}")
async def delete_portfolio(
    id: str,
    _: bool = Depends(require_permission("portfolio", "delete")),
    current_user_id: str = Depends(get_current_user_id)
):
    """删除投资组合（需要删除权限，仅管理员）"""
    # 业务逻辑
    pass
```

## 安全特性

### 1. 账户状态检查
- 自动拒绝未激活账户的访问
- 自动拒绝被锁定账户的访问
- 确保只有有效账户才能执行操作

### 2. 最小权限原则
- 每个角色只拥有其工作所需的最小权限
- Viewer 只能查看，不能修改
- User 可以使用功能，但不能管理系统
- Admin 拥有完全控制权

### 3. 权限验证
- 每次操作都进行权限检查
- 不存在的资源默认拒绝访问
- 不存在的用户默认拒绝访问
- 大小写敏感，防止权限绕过

### 4. 动态权限更新
- 角色变更立即生效
- 无需重启服务
- 支持实时权限调整

## 测试覆盖

授权服务包含全面的单元测试，覆盖以下场景：

### 权限检查测试
- ✅ Viewer 只读权限验证
- ✅ User 读写权限验证
- ✅ Admin 完全权限验证
- ✅ 锁定账户权限拒绝
- ✅ 未激活账户权限拒绝
- ✅ 不存在用户权限拒绝
- ✅ 不存在资源权限拒绝

### 角色管理测试
- ✅ 有效角色分配
- ✅ 无效角色拒绝
- ✅ 角色更新功能
- ✅ 角色变更影响权限
- ✅ 角色查询功能

### 边缘情况测试
- ✅ 空操作处理
- ✅ 大小写敏感性
- ✅ 不存在的资源和用户

**测试结果**：31 个测试全部通过 ✅

## 性能考虑

### 1. 数据库查询优化
- 使用索引加速用户查询（username, email）
- 单次查询获取用户信息和角色
- 避免 N+1 查询问题

### 2. 权限矩阵缓存
- 权限矩阵定义为类常量
- 无需每次查询数据库
- 快速权限检查

### 3. 会话复用
- 使用依赖注入共享数据库会话
- 减少连接开销

## 扩展性

### 添加新资源

在 `PERMISSIONS` 字典中添加新资源：

```python
PERMISSIONS = {
    "viewer": {
        "new_resource": ["read"],
        # ...
    },
    "user": {
        "new_resource": ["read", "write"],
        # ...
    },
    "admin": {
        "new_resource": ["read", "write", "delete"],
        # ...
    }
}
```

### 添加新角色

1. 在 `VALID_ROLES` 列表中添加新角色
2. 在 `PERMISSIONS` 字典中定义角色权限
3. 更新数据库模型（如需要）

### 自定义权限逻辑

可以继承 `AuthorizationService` 并重写方法：

```python
class CustomAuthorizationService(AuthorizationService):
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        # 自定义权限检查逻辑
        if self.is_special_case(user_id, resource):
            return True
        return super().check_permission(user_id, resource, action)
```

## 相关需求

本授权服务实现了以下需求：

- **需求 6.1**：支持基于角色的访问控制（RBAC）
- **需求 6.2**：允许分配特定的角色和权限
- **需求 6.3**：验证用户是否具有相应权限
- **需求 6.4**：权限不足时拒绝操作并提示
- **需求 6.5**：支持权限的动态调整，无需重启服务

## 下一步

1. 集成到 API 路由中（任务 11.4）
2. 实现权限检查中间件（任务 11.1）
3. 编写属性测试验证正确性属性（任务 5.2, 5.3）
4. 添加审计日志记录权限检查事件（任务 8）
