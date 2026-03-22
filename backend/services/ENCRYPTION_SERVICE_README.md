# 加密服务使用指南

## 概述

加密服务模块 (`encryption_service.py`) 提供了数据加密、解密和密码哈希功能，用于保护敏感数据和用户密码。

## 功能特性

### 1. 数据加密（AES-256-GCM）

- **算法**: AES-256-GCM（Galois/Counter Mode）
- **密钥长度**: 256 位（32 字节）
- **认证**: 内置消息认证（防篡改）
- **随机数**: 每次加密使用唯一的 12 字节 nonce

### 2. 密码哈希（bcrypt）

- **算法**: bcrypt
- **工作因子**: 12 轮（推荐的安全级别）
- **盐值**: 自动生成唯一盐值
- **密码限制**: 最大 72 字节（bcrypt 限制）

### 3. 密钥管理

- **生产环境**: 从环境变量 `ENCRYPTION_MASTER_KEY` 加载（Base64 编码）
- **开发环境**: 使用固定的开发密钥（仅用于测试）

## 使用示例

### 基本使用

```python
from services.encryption_service import get_encryption_service

# 获取加密服务实例（单例）
service = get_encryption_service()
```

### 密码哈希和验证

```python
# 哈希密码
password = "MySecurePassword123!"
hashed = service.hash_password(password)
print(f"哈希密码: {hashed}")

# 验证密码
is_valid = service.verify_password(password, hashed)
print(f"密码验证: {is_valid}")  # True

# 验证错误密码
is_invalid = service.verify_password("WrongPassword", hashed)
print(f"错误密码: {is_invalid}")  # False
```

### 数据加密和解密

```python
# 加密字节数据
data = b"Sensitive information"
encrypted = service.encrypt_data(data)

print(f"密文长度: {len(encrypted.ciphertext)}")
print(f"密钥 ID: {encrypted.key_id}")

# 解密数据
decrypted = service.decrypt_data(encrypted)
print(f"解密数据: {decrypted.decode('utf-8')}")
```

### 字符串加密（便捷方法）

```python
# 加密字符串
text = "这是需要加密的文本"
encrypted = service.encrypt_string(text)

# 解密字符串
decrypted_text = service.decrypt_string(encrypted)
print(f"解密文本: {decrypted_text}")
```

### 序列化加密数据

```python
# 加密数据
encrypted = service.encrypt_string("Secret message")

# 序列化为字典（用于 JSON 存储）
encrypted_dict = encrypted.to_dict()

# 反序列化
encrypted_restored = EncryptedData.from_dict(encrypted_dict)

# 解密
decrypted = service.decrypt_string(encrypted_restored)
```

## 环境配置

### 生产环境

在生产环境中，必须设置 `ENCRYPTION_MASTER_KEY` 环境变量：

```bash
# 生成 32 字节随机密钥并 Base64 编码
python3 -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"

# 设置环境变量
export ENCRYPTION_MASTER_KEY="your_base64_encoded_key_here"
export ENVIRONMENT="production"
```

### 开发环境

开发环境会自动使用固定的测试密钥，无需配置。

## 安全注意事项

### 密码哈希

1. **不可逆**: bcrypt 是单向哈希，无法从哈希值恢复原密码
2. **盐值**: 每次哈希自动生成唯一盐值，相同密码的哈希值不同
3. **工作因子**: 使用 12 轮，提供良好的安全性和性能平衡
4. **长度限制**: bcrypt 限制密码最大 72 字节，超长密码会被截断

### 数据加密

1. **认证加密**: GCM 模式提供加密和认证，防止数据被篡改
2. **唯一 nonce**: 每次加密使用新的随机 nonce，确保安全性
3. **密钥管理**: 生产环境必须使用强随机密钥，不要硬编码
4. **密钥轮换**: 定期更换加密密钥以提高安全性

### 最佳实践

1. **密钥存储**: 
   - 使用环境变量或密钥管理服务（如 AWS KMS）
   - 不要将密钥提交到版本控制系统
   - 使用 `.env` 文件并添加到 `.gitignore`

2. **密码策略**:
   - 强制最小密码长度（建议 8-12 字符）
   - 要求包含大小写字母、数字和特殊字符
   - 实施密码过期和历史检查

3. **错误处理**:
   - 不要在错误消息中泄露敏感信息
   - 记录安全事件但不记录密码或密钥
   - 统一认证失败消息，避免用户枚举

## 性能考虑

### bcrypt 性能

- **工作因子 12**: 每次哈希约需 100-300ms
- **适用场景**: 用户登录、密码重置等低频操作
- **不适用**: 高频 API 认证（应使用 JWT 令牌）

### AES-GCM 性能

- **加密速度**: 非常快，适合大数据加密
- **1MB 数据**: 通常在 10ms 内完成
- **适用场景**: 数据库字段加密、文件加密、传输加密

## 测试

运行单元测试：

```bash
python3 test_encryption_service.py
```

测试覆盖：
- ✅ 密码哈希和验证
- ✅ 数据加密和解密
- ✅ 字符串加密
- ✅ 序列化和反序列化
- ✅ 错误密钥处理
- ✅ 数据篡改检测
- ✅ 空数据处理
- ✅ 大数据加密
- ✅ 单例模式
- ✅ 边缘情况

## API 参考

### EncryptionService

#### `hash_password(password: str) -> str`
使用 bcrypt 哈希密码。

**参数**:
- `password`: 明文密码

**返回**: 哈希后的密码字符串

**异常**: `EncryptionError` - 哈希失败

#### `verify_password(password: str, hashed: str) -> bool`
验证密码是否匹配哈希值。

**参数**:
- `password`: 明文密码
- `hashed`: 哈希密码

**返回**: 密码是否匹配

#### `encrypt_data(data: bytes, key_id: str = "master") -> EncryptedData`
使用 AES-256-GCM 加密数据。

**参数**:
- `data`: 要加密的字节数据
- `key_id`: 密钥 ID（默认 "master"）

**返回**: `EncryptedData` 对象

**异常**: `EncryptionError` - 加密失败

#### `decrypt_data(encrypted_data: EncryptedData) -> bytes`
使用 AES-256-GCM 解密数据。

**参数**:
- `encrypted_data`: 加密的数据对象

**返回**: 解密后的字节数据

**异常**: `DecryptionError` - 解密失败

#### `encrypt_string(text: str, key_id: str = "master") -> EncryptedData`
加密字符串（便捷方法）。

#### `decrypt_string(encrypted_data: EncryptedData) -> str`
解密字符串（便捷方法）。

### EncryptedData

加密数据容器类。

**属性**:
- `ciphertext`: 密文（bytes）
- `nonce`: 随机数（bytes）
- `tag`: 认证标签（bytes）
- `key_id`: 密钥 ID（str）
- `algorithm`: 加密算法（str）

**方法**:
- `to_dict()`: 序列化为字典
- `from_dict(data)`: 从字典反序列化

## 相关需求

- **需求 5.2**: 数据传输安全 - 使用强加密算法

## 更新日志

- **2024-01**: 初始实现
  - AES-256-GCM 数据加密
  - bcrypt 密码哈希
  - 密钥管理
  - 完整的单元测试
