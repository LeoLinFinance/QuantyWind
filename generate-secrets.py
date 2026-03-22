#!/usr/bin/env python3
"""
生成安全的随机密钥
用于配置 .env 文件中的密钥
"""
import secrets
import string

def generate_password(length=16):
    """生成强密码"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def generate_secret_key(length=32):
    """生成 URL 安全的密钥"""
    return secrets.token_urlsafe(length)

def generate_encryption_key():
    """生成 32 字节的加密密钥"""
    return secrets.token_urlsafe(32)

def main():
    print("=" * 60)
    print("量数风行 - 安全密钥生成器")
    print("=" * 60)
    print()
    
    print("请将以下生成的密钥复制到 .env 文件中：")
    print()
    
    print("# 数据库密码")
    print(f"POSTGRES_PASSWORD={generate_password(20)}")
    print()
    
    print("# Redis 密码")
    print(f"REDIS_PASSWORD={generate_password(20)}")
    print()
    
    print("# 应用密钥")
    print(f"SECRET_KEY={generate_secret_key(32)}")
    print()
    
    print("# JWT 密钥")
    print(f"JWT_SECRET_KEY={generate_secret_key(32)}")
    print()
    
    print("# 加密密钥（32 字节）")
    print(f"ENCRYPTION_KEY={generate_encryption_key()}")
    print()
    
    print("=" * 60)
    print("注意事项：")
    print("1. 请妥善保管这些密钥，不要提交到版本控制")
    print("2. 每个环境（开发、测试、生产）应使用不同的密钥")
    print("3. 定期更换密钥以提高安全性")
    print("4. 如果密钥泄露，立即更换并重新部署")
    print("=" * 60)

if __name__ == "__main__":
    main()
