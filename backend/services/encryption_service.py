"""
加密服务模块

提供数据加密、解密和密码哈希功能。
- AES-256-GCM 数据加密和解密
- bcrypt 密码哈希和验证
- 密钥管理（从环境变量加载）

需求：5.2
"""

import os
import base64
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import bcrypt


class EncryptionError(Exception):
    """加密操作异常"""
    pass


class DecryptionError(Exception):
    """解密操作异常"""
    pass


class EncryptedData:
    """加密数据容器"""
    
    def __init__(self, ciphertext: bytes, nonce: bytes, tag: bytes, key_id: str, algorithm: str = "AES-256-GCM"):
        """
        初始化加密数据对象
        
        参数:
            ciphertext: 密文
            nonce: 随机数（初始化向量）
            tag: 认证标签（GCM 模式）
            key_id: 密钥 ID
            algorithm: 加密算法
        """
        self.ciphertext = ciphertext
        self.nonce = nonce
        self.tag = tag
        self.key_id = key_id
        self.algorithm = algorithm
    
    def to_dict(self) -> dict:
        """转换为字典格式（用于序列化）"""
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(self.nonce).decode('utf-8'),
            "tag": base64.b64encode(self.tag).decode('utf-8'),
            "key_id": self.key_id,
            "algorithm": self.algorithm
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EncryptedData':
        """从字典创建对象（用于反序列化）"""
        return cls(
            ciphertext=base64.b64decode(data["ciphertext"]),
            nonce=base64.b64decode(data["nonce"]),
            tag=base64.b64decode(data["tag"]),
            key_id=data["key_id"],
            algorithm=data.get("algorithm", "AES-256-GCM")
        )


class EncryptionService:
    """
    加密服务
    
    提供数据加密、解密和密码哈希功能。
    """
    
    def __init__(self):
        """初始化加密服务"""
        # bcrypt 工作因子（12 轮）
        self.bcrypt_rounds = 12
        
        # 密钥存储（从环境变量加载）
        self._keys = {}
        self._load_keys()
    
    def _load_keys(self) -> None:
        """从环境变量加载加密密钥"""
        # 加载主密钥
        master_key_b64 = os.getenv("ENCRYPTION_MASTER_KEY")
        if master_key_b64:
            try:
                master_key = base64.b64decode(master_key_b64)
                if len(master_key) != 32:  # AES-256 需要 32 字节密钥
                    raise ValueError("Master key must be 32 bytes (256 bits)")
                self._keys["master"] = master_key
            except Exception as e:
                raise EncryptionError(f"Failed to load master key: {str(e)}")
        else:
            # 开发环境：生成临时密钥（生产环境必须设置环境变量）
            if os.getenv("ENVIRONMENT") == "production":
                raise EncryptionError("ENCRYPTION_MASTER_KEY must be set in production")
            # 使用固定的开发密钥（仅用于开发/测试）- 正好 32 字节
            self._keys["master"] = b"dev_master_key_32bytes_test!!"[:32].ljust(32, b'0')
    
    def _get_key(self, key_id: str) -> bytes:
        """
        获取指定的加密密钥
        
        参数:
            key_id: 密钥 ID
        
        返回:
            bytes: 密钥
        
        异常:
            EncryptionError: 密钥不存在
        """
        if key_id not in self._keys:
            raise EncryptionError(f"Key '{key_id}' not found")
        return self._keys[key_id]
    
    def encrypt_data(self, data: bytes, key_id: str = "master") -> EncryptedData:
        """
        使用 AES-256-GCM 加密数据
        
        参数:
            data: 要加密的数据
            key_id: 加密密钥 ID（默认使用主密钥）
        
        返回:
            EncryptedData: 加密后的数据（包含 nonce 和 tag）
        
        异常:
            EncryptionError: 加密失败
        """
        try:
            # 获取密钥
            key = self._get_key(key_id)
            
            # 创建 AESGCM 实例
            aesgcm = AESGCM(key)
            
            # 生成随机 nonce（12 字节是 GCM 模式的标准长度）
            nonce = os.urandom(12)
            
            # 加密数据（GCM 模式会自动生成认证标签）
            ciphertext_with_tag = aesgcm.encrypt(nonce, data, None)
            
            # GCM 模式的输出格式：ciphertext + tag（最后 16 字节）
            ciphertext = ciphertext_with_tag[:-16]
            tag = ciphertext_with_tag[-16:]
            
            return EncryptedData(
                ciphertext=ciphertext,
                nonce=nonce,
                tag=tag,
                key_id=key_id,
                algorithm="AES-256-GCM"
            )
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """
        使用 AES-256-GCM 解密数据
        
        参数:
            encrypted_data: 加密的数据
        
        返回:
            bytes: 解密后的数据
        
        异常:
            DecryptionError: 解密失败（密钥错误或数据被篡改）
        """
        try:
            # 获取密钥
            key = self._get_key(encrypted_data.key_id)
            
            # 创建 AESGCM 实例
            aesgcm = AESGCM(key)
            
            # 重组密文和标签
            ciphertext_with_tag = encrypted_data.ciphertext + encrypted_data.tag
            
            # 解密数据（会自动验证认证标签）
            plaintext = aesgcm.decrypt(encrypted_data.nonce, ciphertext_with_tag, None)
            
            return plaintext
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """
        使用 bcrypt 哈希密码
        
        参数:
            password: 明文密码
        
        返回:
            str: 哈希后的密码（包含盐值）
        
        异常:
            EncryptionError: 哈希失败
        
        注意:
            bcrypt 有 72 字节的密码长度限制。
            超过此长度的密码将被截断。
        """
        try:
            # 将密码转换为字节
            password_bytes = password.encode('utf-8')
            
            # bcrypt 限制：密码最多 72 字节
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            # 生成盐值并哈希
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            hashed = bcrypt.hashpw(password_bytes, salt)
            
            # 返回字符串格式
            return hashed.decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Password hashing failed: {str(e)}")
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        验证密码是否匹配哈希值
        
        参数:
            password: 明文密码
            hashed: 哈希密码
        
        返回:
            bool: 密码是否匹配
        
        注意:
            bcrypt 有 72 字节的密码长度限制。
            超过此长度的密码将被截断后验证。
        """
        try:
            password_bytes = password.encode('utf-8')
            
            # bcrypt 限制：密码最多 72 字节
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            hashed_bytes = hashed.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            # 验证失败（可能是格式错误）
            return False
    
    def encrypt_string(self, text: str, key_id: str = "master") -> EncryptedData:
        """
        加密字符串（便捷方法）
        
        参数:
            text: 要加密的字符串
            key_id: 加密密钥 ID
        
        返回:
            EncryptedData: 加密后的数据
        """
        return self.encrypt_data(text.encode('utf-8'), key_id)
    
    def decrypt_string(self, encrypted_data: EncryptedData) -> str:
        """
        解密字符串（便捷方法）
        
        参数:
            encrypted_data: 加密的数据
        
        返回:
            str: 解密后的字符串
        """
        plaintext = self.decrypt_data(encrypted_data)
        return plaintext.decode('utf-8')


# 全局单例实例
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    获取加密服务单例实例
    
    返回:
        EncryptionService: 加密服务实例
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
