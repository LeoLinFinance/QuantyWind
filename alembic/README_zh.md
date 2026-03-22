# Alembic 数据库迁移

本目录包含安全远程访问部署系统的数据库迁移脚本。

## 概述

使用 Alembic 管理数据库架构的版本控制和迁移。迁移脚本定义了数据库架构的变更，可以向前（upgrade）或向后（downgrade）应用。

## 数据库表

初始迁移创建以下表：

### 1. users（用户表）
- 存储用户账户信息
- 包含身份验证、角色和安全状态
- 索引：username, email

### 2. sessions（会话表）
- 存储用户会话信息
- 包含令牌、IP 地址和过期时间
- 索引：user_id, token
- 外键：user_id -> users.id（级联删除）

### 3. audit_logs（审计日志表）
- 记录所有安全相关事件
- 包含身份验证、授权和系统操作
- 索引：event_type, user_id, timestamp
- 复合索引：
  - (user_id, timestamp)
  - (event_type, timestamp)
  - (severity, timestamp)

### 4. licenses（许可证表）
- 管理用户许可证
- 包含类型、状态和过期时间
- 索引：user_id, license_key
- 复合索引：(status, expires_at)
- 外键：user_id -> users.id（级联删除）

## 使用方法

### 前置条件

1. 确保 PostgreSQL 数据库正在运行
2. 在 `.env` 文件中配置数据库连接：
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   ```

### 应用迁移

从项目根目录运行：

```bash
# 查看当前迁移状态
alembic current

# 查看迁移历史
alembic history

# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade <revision_id>

# 降级一个版本
alembic downgrade -1

# 降级到特定版本
alembic downgrade <revision_id>

# 降级到初始状态
alembic downgrade base
```

### 创建新迁移

```bash
# 手动创建迁移
alembic revision -m "描述迁移内容"

# 自动生成迁移（需要数据库连接）
alembic revision --autogenerate -m "描述迁移内容"
```

### 生成 SQL 脚本（不执行）

```bash
# 生成升级 SQL
alembic upgrade head --sql > upgrade.sql

# 生成降级 SQL
alembic downgrade -1 --sql > downgrade.sql
```

## 索引优化

迁移脚本包含以下索引以优化查询性能：

### 单列索引
- `users.username` - 用于登录查询
- `users.email` - 用于邮箱查询
- `sessions.user_id` - 用于查询用户会话
- `sessions.token` - 用于令牌验证
- `audit_logs.event_type` - 用于按事件类型查询
- `audit_logs.user_id` - 用于查询用户操作
- `audit_logs.timestamp` - 用于时间范围查询
- `licenses.user_id` - 用于查询用户许可证
- `licenses.license_key` - 用于许可证验证

### 复合索引
- `audit_logs(user_id, timestamp)` - 优化用户操作历史查询
- `audit_logs(event_type, timestamp)` - 优化事件类型时间序列查询
- `audit_logs(severity, timestamp)` - 优化安全事件查询
- `licenses(status, expires_at)` - 优化许可证状态和过期查询

## 注意事项

1. **备份数据库**：在应用迁移前，始终备份生产数据库
2. **测试迁移**：在开发/测试环境中先测试迁移
3. **版本控制**：迁移脚本应纳入版本控制
4. **不要修改已应用的迁移**：如需更改，创建新的迁移脚本
5. **环境变量**：确保 `DATABASE_URL` 正确配置

## 故障排查

### 连接错误
如果遇到数据库连接错误：
1. 检查 PostgreSQL 是否运行
2. 验证 `.env` 文件中的数据库凭证
3. 确认数据库已创建
4. 检查防火墙设置

### 迁移冲突
如果遇到迁移冲突：
1. 使用 `alembic current` 查看当前状态
2. 使用 `alembic history` 查看迁移历史
3. 必要时使用 `alembic stamp <revision>` 手动设置版本

### 回滚迁移
如果迁移失败：
1. 使用 `alembic downgrade -1` 回滚
2. 检查错误日志
3. 修复问题后重新应用

## 相关文件

- `alembic.ini` - Alembic 配置文件
- `alembic/env.py` - 迁移环境配置
- `alembic/versions/` - 迁移脚本目录
- `backend/database/config.py` - 数据库连接配置
- `backend/models/` - SQLAlchemy 模型定义

## 参考资料

- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
