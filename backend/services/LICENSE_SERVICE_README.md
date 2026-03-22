# 许可证管理服务 (License Service)

## 概述

许可证管理服务负责管理用户许可证的完整生命周期，包括验证、激活、续期、暂停和使用记录。该服务是安全远程访问部署系统的核心组件之一。

## 功能特性

### 1. 许可证验证
- 验证用户许可证的有效性和状态
- 自动检测并更新过期许可证状态
- 记录许可证使用情况

### 2. 许可证激活
- 支持通过许可证密钥激活
- 验证密钥格式和唯一性
- 防止重复激活

### 3. 许可证到期检查
- 计算剩余有效天数
- 支持到期提醒（默认提前7天）
- 自动识别即将到期的许可证

### 4. 许可证使用记录
- 记录所有许可证相关操作
- 集成审计日志系统
- 支持使用情况分析

### 5. 许可证管理
- 创建不同类型的许可证（试用版、标准版、企业版）
- 续期许可证
- 暂停和重新激活许可证
- 功能访问控制

## 许可证类型

### Trial（试用版）
- 有效期：30天
- 最大会话数：1
- 功能：portfolio, market_data, risk_analysis

### Standard（标准版）
- 有效期：365天
- 最大会话数：3
- 功能：portfolio, market_data, risk_analysis, sentiment_map, ai_signals, news

### Enterprise（企业版）
- 有效期：365天
- 最大会话数：10
- 功能：所有功能 + expert_forum, advanced_analytics, api_access

## API 接口

### 验证许可证
```python
status = license_service.validate_license(user_id)
# 返回: "active", "expired", "suspended"
```

### 激活许可证
```python
license_obj = license_service.activate_license(user_id, license_key)
```

### 检查到期时间
```python
days_remaining = license_service.check_expiration(user_id)
# 返回: 剩余天数（负数表示已过期）
```

### 创建许可证（管理员）
```python
license_obj = license_service.create_license(
    user_id,
    license_type="standard",
    duration_days=365  # 可选
)
```

### 续期许可证
```python
license_obj = license_service.renew_license(
    user_id,
    duration_days=365  # 可选
)
```

### 暂停许可证
```python
license_obj = license_service.suspend_license(user_id, reason="Payment overdue")
```

### 重新激活许可证
```python
license_obj = license_service.reactivate_license(user_id)
```

### 检查功能访问权限
```python
has_access = license_service.has_feature_access(user_id, "expert_forum")
```

### 获取到期提醒列表
```python
warnings = license_service.check_expiration_warnings()
# 返回即将到期（7天内）的许可证列表
```

### 获取许可证统计
```python
stats = license_service.get_license_statistics()
# 返回: {
#   "total_licenses": 100,
#   "active": 85,
#   "expired": 10,
#   "suspended": 5,
#   "by_type": {"trial": 20, "standard": 60, "enterprise": 20},
#   "expiring_soon": 5
# }
```

## 许可证密钥格式

许可证密钥格式：`XXXX-XXXX-XXXX-XXXX`
- 4段，每段4个字符
- 支持字母（大小写）和数字
- 使用连字符分隔

示例：
- `ABCD-1234-EFGH-5678`
- `a1b2-c3d4-e5f6-g7h8`

## 异常处理

### LicenseError
许可证相关错误的基类

### InvalidLicenseKeyError
许可证密钥无效（格式错误或不存在）

### LicenseAlreadyUsedError
许可证已被使用（用户已有许可证或密钥已被使用）

### LicenseExpiredError
许可证已过期

### LicenseSuspendedError
许可证已暂停

## 使用示例

### 基本使用流程

```python
from backend.services.license_service import get_license_service
from backend.database.config import get_db

# 获取服务实例
db = next(get_db())
license_service = get_license_service(db)

# 1. 创建许可证（管理员）
license = license_service.create_license(
    user_id="user_123",
    license_type="standard"
)
print(f"Created license: {license.license_key}")

# 2. 验证许可证
status = license_service.validate_license("user_123")
print(f"License status: {status}")

# 3. 检查到期时间
days = license_service.check_expiration("user_123")
print(f"Days remaining: {days}")

# 4. 检查功能访问
if license_service.has_feature_access("user_123", "expert_forum"):
    print("User has access to expert forum")

# 5. 续期许可证
renewed = license_service.renew_license("user_123", duration_days=180)
print(f"License renewed until: {renewed.expires_at}")
```

### 用户激活许可证

```python
try:
    license = license_service.activate_license(
        user_id="user_456",
        license_key="ABCD-1234-EFGH-5678"
    )
    print(f"License activated successfully!")
    print(f"Type: {license.license_type}")
    print(f"Expires: {license.expires_at}")
except InvalidLicenseKeyError:
    print("Invalid license key format")
except LicenseAlreadyUsedError:
    print("License key already used or user already has a license")
```

### 管理员检查到期提醒

```python
# 获取即将到期的许可证
warnings = license_service.check_expiration_warnings()

for warning in warnings:
    print(f"User {warning['user_id']} license expires in {warning['days_remaining']} days")
    # 发送提醒邮件给用户
    send_expiration_email(warning['user_id'], warning['days_remaining'])
```

## 审计日志集成

许可证服务自动记录以下事件到审计日志：

- `license_activated`: 许可证激活
- `license_renewed`: 许可证续期
- `license_suspended`: 许可证暂停
- `license_reactivated`: 许可证重新激活
- `license_expired`: 许可证过期
- `license_expiration_warning`: 到期提醒
- `license_usage`: 许可证使用（验证、功能访问等）

所有事件都包含详细的元数据，便于审计和分析。

## 测试

运行单元测试：
```bash
python3 -m pytest tests/test_license_service.py -v
```

测试覆盖：
- 许可证密钥生成和验证
- 许可证验证（活动、过期、暂停）
- 许可证激活（有效、无效、重复）
- 许可证创建（不同类型、自定义时长）
- 许可证到期检查
- 许可证续期
- 许可证暂停和重新激活
- 到期提醒
- 功能访问控制
- 许可证统计
- 边缘情况处理

## 安全考虑

1. **密钥唯一性**：每个许可证密钥全局唯一
2. **防重复激活**：用户只能有一个活动许可证
3. **审计日志**：所有操作都被记录
4. **自动过期**：过期许可证自动失效
5. **功能隔离**：基于许可证类型的功能访问控制

## 性能优化

1. 许可证数据存储在数据库中，支持索引查询
2. 使用审计日志服务记录使用情况，避免重复查询
3. 到期检查使用数据库查询优化，避免全表扫描

## 未来改进

1. 支持许可证转移（从一个用户转移到另一个用户）
2. 支持许可证降级/升级
3. 支持许可证使用量限制（如 API 调用次数）
4. 支持许可证批量管理
5. 支持许可证自动续期（订阅模式）

## 相关文档

- [需求文档](../../.kiro/specs/secure-remote-deployment/requirements.md) - 需求 12.1-12.5
- [设计文档](../../.kiro/specs/secure-remote-deployment/design.md) - 许可证管理服务设计
- [审计日志服务](./AUDIT_LOG_SERVICE_README.md)
- [用户模型](../models/user.py)
- [许可证模型](../models/license.py)
