"""
加密服务单元测试

测试 AES-256-GCM 加密、bcrypt 密码哈希等功能
"""

import os
import sys

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.encryption_service import (
    EncryptionService,
    EncryptedData,
    EncryptionError,
    DecryptionError,
    get_encryption_service
)


def test_password_hashing():
    """测试密码哈希和验证"""
    print("\n" + "=" * 60)
    print("测试 1: 密码哈希和验证")
    print("=" * 60)
    
    service = EncryptionService()
    
    # 测试密码哈希
    password = "MySecurePassword123!"
    hashed = service.hash_password(password)
    
    print(f"原始密码: {password}")
    print(f"哈希密码: {hashed[:60]}...")
    print(f"哈希长度: {len(hashed)} 字符")
    
    # 验证正确的密码
    is_valid = service.verify_password(password, hashed)
    print(f"✓ 正确密码验证: {is_valid}")
    assert is_valid, "正确密码应该验证通过"
    
    # 验证错误的密码
    is_invalid = service.verify_password("WrongPassword", hashed)
    print(f"✓ 错误密码验证: {is_invalid}")
    assert not is_invalid, "错误密码应该验证失败"
    
    # 测试每次哈希结果不同（因为盐值不同）
    hashed2 = service.hash_password(password)
    print(f"✓ 两次哈希结果不同: {hashed != hashed2}")
    assert hashed != hashed2, "相同密码的两次哈希应该不同"
    
    # 但两个哈希都应该能验证原密码
    assert service.verify_password(password, hashed2), "第二个哈希也应该能验证原密码"
    
    print("✅ 密码哈希测试通过")


def test_data_encryption_decryption():
    """测试数据加密和解密"""
    print("\n" + "=" * 60)
    print("测试 2: 数据加密和解密")
    print("=" * 60)
    
    service = EncryptionService()
    
    # 测试字节数据加密
    original_data = b"This is sensitive data that needs encryption!"
    print(f"原始数据: {original_data.decode('utf-8')}")
    
    # 加密
    encrypted = service.encrypt_data(original_data)
    print(f"✓ 加密成功")
    print(f"  - 密文长度: {len(encrypted.ciphertext)} 字节")
    print(f"  - Nonce 长度: {len(encrypted.nonce)} 字节")
    print(f"  - Tag 长度: {len(encrypted.tag)} 字节")
    print(f"  - 密钥 ID: {encrypted.key_id}")
    print(f"  - 算法: {encrypted.algorithm}")
    
    # 解密
    decrypted = service.decrypt_data(encrypted)
    print(f"✓ 解密成功")
    print(f"解密数据: {decrypted.decode('utf-8')}")
    
    # 验证数据一致性
    assert decrypted == original_data, "解密后的数据应该与原始数据一致"
    print("✅ 加密解密往返测试通过")


def test_string_encryption():
    """测试字符串加密（便捷方法）"""
    print("\n" + "=" * 60)
    print("测试 3: 字符串加密")
    print("=" * 60)
    
    service = EncryptionService()
    
    original_text = "这是一段需要加密的中文文本！"
    print(f"原始文本: {original_text}")
    
    # 加密
    encrypted = service.encrypt_string(original_text)
    print(f"✓ 加密成功")
    
    # 解密
    decrypted_text = service.decrypt_string(encrypted)
    print(f"✓ 解密成功")
    print(f"解密文本: {decrypted_text}")
    
    # 验证
    assert decrypted_text == original_text, "解密后的文本应该与原始文本一致"
    print("✅ 字符串加密测试通过")


def test_encrypted_data_serialization():
    """测试加密数据的序列化和反序列化"""
    print("\n" + "=" * 60)
    print("测试 4: 加密数据序列化")
    print("=" * 60)
    
    service = EncryptionService()
    
    original_text = "Test data for serialization"
    print(f"原始文本: {original_text}")
    
    # 加密
    encrypted = service.encrypt_string(original_text)
    
    # 序列化为字典
    encrypted_dict = encrypted.to_dict()
    print(f"✓ 序列化为字典")
    print(f"  - 字典键: {list(encrypted_dict.keys())}")
    
    # 反序列化
    encrypted_restored = EncryptedData.from_dict(encrypted_dict)
    print(f"✓ 从字典反序列化")
    
    # 解密恢复的数据
    decrypted_text = service.decrypt_string(encrypted_restored)
    print(f"✓ 解密成功")
    print(f"解密文本: {decrypted_text}")
    
    # 验证
    assert decrypted_text == original_text, "序列化往返后数据应该一致"
    print("✅ 序列化测试通过")


def test_encryption_with_wrong_key():
    """测试使用错误密钥解密"""
    print("\n" + "=" * 60)
    print("测试 5: 错误密钥解密（应该失败）")
    print("=" * 60)
    
    service = EncryptionService()
    
    original_text = "Secret message"
    encrypted = service.encrypt_string(original_text)
    
    # 篡改密钥 ID（模拟使用错误密钥）
    encrypted.key_id = "wrong_key"
    
    try:
        service.decrypt_string(encrypted)
        print("❌ 应该抛出异常但没有")
        assert False, "使用错误密钥应该解密失败"
    except DecryptionError as e:
        print(f"✓ 正确抛出 DecryptionError: {str(e)}")
        print("✅ 错误密钥测试通过")


def test_data_tampering_detection():
    """测试数据篡改检测"""
    print("\n" + "=" * 60)
    print("测试 6: 数据篡改检测")
    print("=" * 60)
    
    service = EncryptionService()
    
    original_text = "Important data"
    encrypted = service.encrypt_string(original_text)
    
    # 篡改密文
    tampered_ciphertext = bytearray(encrypted.ciphertext)
    tampered_ciphertext[0] ^= 0xFF  # 翻转第一个字节
    encrypted.ciphertext = bytes(tampered_ciphertext)
    
    try:
        service.decrypt_string(encrypted)
        print("❌ 应该检测到篡改但没有")
        assert False, "篡改的数据应该解密失败"
    except DecryptionError as e:
        print(f"✓ 正确检测到篡改: {str(e)}")
        print("✅ 篡改检测测试通过")


def test_empty_data():
    """测试空数据加密"""
    print("\n" + "=" * 60)
    print("测试 7: 空数据加密")
    print("=" * 60)
    
    service = EncryptionService()
    
    # 测试空字节
    empty_data = b""
    encrypted = service.encrypt_data(empty_data)
    decrypted = service.decrypt_data(encrypted)
    
    assert decrypted == empty_data, "空数据应该能正确加密解密"
    print("✓ 空字节数据测试通过")
    
    # 测试空字符串
    empty_string = ""
    encrypted = service.encrypt_string(empty_string)
    decrypted = service.decrypt_string(encrypted)
    
    assert decrypted == empty_string, "空字符串应该能正确加密解密"
    print("✓ 空字符串测试通过")
    
    print("✅ 空数据测试通过")


def test_large_data():
    """测试大数据加密"""
    print("\n" + "=" * 60)
    print("测试 8: 大数据加密")
    print("=" * 60)
    
    service = EncryptionService()
    
    # 生成 1MB 的数据
    large_data = b"X" * (1024 * 1024)
    print(f"数据大小: {len(large_data) / 1024 / 1024:.2f} MB")
    
    # 加密
    encrypted = service.encrypt_data(large_data)
    print(f"✓ 加密成功")
    
    # 解密
    decrypted = service.decrypt_data(encrypted)
    print(f"✓ 解密成功")
    
    # 验证
    assert decrypted == large_data, "大数据应该能正确加密解密"
    print("✅ 大数据测试通过")


def test_singleton_service():
    """测试单例服务"""
    print("\n" + "=" * 60)
    print("测试 9: 单例服务")
    print("=" * 60)
    
    service1 = get_encryption_service()
    service2 = get_encryption_service()
    
    assert service1 is service2, "应该返回同一个实例"
    print("✓ 单例模式正常工作")
    print("✅ 单例测试通过")


def test_password_edge_cases():
    """测试密码边缘情况"""
    print("\n" + "=" * 60)
    print("测试 10: 密码边缘情况")
    print("=" * 60)
    
    service = EncryptionService()
    
    # 测试特殊字符
    special_password = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
    hashed = service.hash_password(special_password)
    assert service.verify_password(special_password, hashed)
    print("✓ 特殊字符密码测试通过")
    
    # 测试 Unicode 字符
    unicode_password = "密码123パスワード🔐"
    hashed = service.hash_password(unicode_password)
    assert service.verify_password(unicode_password, hashed)
    print("✓ Unicode 密码测试通过")
    
    # 测试很长的密码
    long_password = "a" * 1000
    hashed = service.hash_password(long_password)
    assert service.verify_password(long_password, hashed)
    print("✓ 长密码测试通过")
    
    # 测试验证无效的哈希格式
    invalid_hash = "not_a_valid_hash"
    assert not service.verify_password("password", invalid_hash)
    print("✓ 无效哈希格式测试通过")
    
    print("✅ 密码边缘情况测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始加密服务测试")
    print("=" * 60)
    
    try:
        test_password_hashing()
        test_data_encryption_decryption()
        test_string_encryption()
        test_encrypted_data_serialization()
        test_encryption_with_wrong_key()
        test_data_tampering_detection()
        test_empty_data()
        test_large_data()
        test_singleton_service()
        test_password_edge_cases()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return True
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
