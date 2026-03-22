"""
许可证管理服务单元测试

测试许可证验证、激活、到期检查、使用记录和到期提醒功能
"""

import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from backend.database.config import Base
from backend.models.user import User
from backend.models.license import License
from backend.models.audit_log import AuditLog
from backend.services.license_service import (
    LicenseService,
    LicenseError,
    InvalidLicenseKeyError,
    LicenseAlreadyUsedError,
    LicenseExpiredError,
    LicenseStatus,
    LicenseType
)


# 测试数据库设置
@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def license_service(db_session):
    """创建许可证服务实例"""
    return LicenseService(db_session)


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role="user",
        is_active=True,
        is_locked=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_license(db_session, test_user):
    """创建测试许可证"""
    now = datetime.now(timezone.utc)
    license_obj = License(
        user_id=test_user.id,
        license_key="ABCD-1234-EFGH-5678",
        license_type=LicenseType.STANDARD,
        status=LicenseStatus.ACTIVE,
        issued_at=now,
        expires_at=now + timedelta(days=365),
        max_sessions=3,
        features=["portfolio", "market_data", "risk_analysis"]
    )
    db_session.add(license_obj)
    db_session.commit()
    db_session.refresh(license_obj)
    return license_obj


class TestLicenseKeyGeneration:
    """测试许可证密钥生成"""
    
    def test_generate_license_key_format(self, license_service):
        """测试生成的许可证密钥格式正确"""
        key = license_service._generate_license_key()
        
        # 验证格式：XXXX-XXXX-XXXX-XXXX
        parts = key.split("-")
        assert len(parts) == 4
        
        for part in parts:
            assert len(part) == 4
            assert all(c in "0123456789ABCDEF" for c in part)
    
    def test_generate_unique_keys(self, license_service):
        """测试生成的密钥是唯一的"""
        keys = set()
        for _ in range(100):
            key = license_service._generate_license_key()
            keys.add(key)
        
        # 100 个密钥应该都是唯一的
        assert len(keys) == 100
    
    def test_validate_license_key_format_valid(self, license_service):
        """测试有效的许可证密钥格式验证"""
        valid_keys = [
            "ABCD-1234-EFGH-5678",
            "0000-0000-0000-0000",
            "FFFF-FFFF-FFFF-FFFF"
        ]
        
        for key in valid_keys:
            assert license_service._validate_license_key_format(key) is True
    
    def test_validate_license_key_format_invalid(self, license_service):
        """测试无效的许可证密钥格式验证"""
        invalid_keys = [
            "ABCD-1234-EFGH",  # 缺少一段
            "ABCD-1234-EFGH-5678-9012",  # 多一段
            "ABCD-123-EFGH-5678",  # 段长度不对
            "ABCD 1234 EFGH 5678",  # 使用空格而不是连字符
            "ABCD-1234-EFGH-567!",  # 包含特殊字符
            "ABCD-1234-EFGH-567@",  # 包含特殊字符
        ]
        
        for key in invalid_keys:
            assert license_service._validate_license_key_format(key) is False


class TestLicenseValidation:
    """测试许可证验证"""
    
    def test_validate_active_license(self, license_service, test_user, test_license):
        """测试验证活动许可证"""
        status = license_service.validate_license(test_user.id)
        assert status == LicenseStatus.ACTIVE
    
    def test_validate_nonexistent_license(self, license_service, test_user):
        """测试验证不存在的许可证"""
        with pytest.raises(LicenseError, match="没有许可证"):
            license_service.validate_license(test_user.id)
    
    def test_validate_expired_license(self, license_service, db_session, test_user):
        """测试验证已过期的许可证"""
        # 创建已过期的许可证
        now = datetime.now(timezone.utc)
        expired_license = License(
            user_id=test_user.id,
            license_key="DEAD-BEEF-CAFE-BABE",
            license_type=LicenseType.TRIAL,
            status=LicenseStatus.ACTIVE,
            issued_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=1),  # 昨天过期
            max_sessions=1,
            features=["portfolio"]
        )
        db_session.add(expired_license)
        db_session.commit()
        
        # 验证许可证
        status = license_service.validate_license(test_user.id)
        
        # 应该返回过期状态
        assert status == LicenseStatus.EXPIRED
        
        # 数据库中的状态应该被更新
        db_session.refresh(expired_license)
        assert expired_license.status == LicenseStatus.EXPIRED
    
    def test_validate_suspended_license(self, license_service, test_license):
        """测试验证已暂停的许可证"""
        # 暂停许可证
        test_license.status = LicenseStatus.SUSPENDED
        license_service.db.commit()
        
        # 验证许可证
        status = license_service.validate_license(test_license.user_id)
        assert status == LicenseStatus.SUSPENDED


class TestLicenseActivation:
    """测试许可证激活"""
    
    def test_activate_valid_license(self, license_service, test_user):
        """测试激活有效的许可证"""
        license_key = "1234-5678-ABCD-EFGH"
        
        license_obj = license_service.activate_license(test_user.id, license_key)
        
        assert license_obj is not None
        assert license_obj.user_id == test_user.id
        assert license_obj.license_key == license_key
        assert license_obj.status == LicenseStatus.ACTIVE
        assert license_obj.license_type == LicenseType.STANDARD
    
    def test_activate_invalid_format(self, license_service, test_user):
        """测试激活格式无效的许可证"""
        invalid_key = "invalid-key"
        
        with pytest.raises(InvalidLicenseKeyError, match="格式无效"):
            license_service.activate_license(test_user.id, invalid_key)
    
    def test_activate_duplicate_license(self, license_service, test_user, test_license):
        """测试用户已有许可证时激活"""
        new_key = "9999-8888-7777-6666"
        
        with pytest.raises(LicenseAlreadyUsedError, match="已有许可证"):
            license_service.activate_license(test_user.id, new_key)
    
    def test_activate_used_key(self, license_service, db_session, test_license):
        """测试激活已被使用的许可证密钥"""
        # 创建另一个用户
        another_user = User(
            username="anotheruser",
            email="another@example.com",
            password_hash="hashed",
            role="user",
            is_active=True
        )
        db_session.add(another_user)
        db_session.commit()
        
        # 尝试使用已存在的许可证密钥
        with pytest.raises(LicenseAlreadyUsedError, match="已被使用"):
            license_service.activate_license(another_user.id, test_license.license_key)
    
    def test_activate_nonexistent_user(self, license_service):
        """测试为不存在的用户激活许可证"""
        fake_user_id = "nonexistent-user-id"
        license_key = "1234-5678-ABCD-EFGH"
        
        with pytest.raises(LicenseError, match="不存在"):
            license_service.activate_license(fake_user_id, license_key)


class TestLicenseCreation:
    """测试许可证创建（管理员功能）"""
    
    def test_create_trial_license(self, license_service, test_user):
        """测试创建试用版许可证"""
        license_obj = license_service.create_license(
            test_user.id,
            LicenseType.TRIAL
        )
        
        assert license_obj.license_type == LicenseType.TRIAL
        assert license_obj.max_sessions == 1
        assert "portfolio" in license_obj.features
        
        # 验证有效期
        days_remaining = license_obj.days_until_expiration()
        assert 29 <= days_remaining <= 30  # 允许一天的误差
    
    def test_create_standard_license(self, license_service, test_user):
        """测试创建标准版许可证"""
        license_obj = license_service.create_license(
            test_user.id,
            LicenseType.STANDARD
        )
        
        assert license_obj.license_type == LicenseType.STANDARD
        assert license_obj.max_sessions == 3
        assert "ai_signals" in license_obj.features
    
    def test_create_enterprise_license(self, license_service, test_user):
        """测试创建企业版许可证"""
        license_obj = license_service.create_license(
            test_user.id,
            LicenseType.ENTERPRISE
        )
        
        assert license_obj.license_type == LicenseType.ENTERPRISE
        assert license_obj.max_sessions == 10
        assert "expert_forum" in license_obj.features
        assert "api_access" in license_obj.features
    
    def test_create_license_custom_duration(self, license_service, test_user):
        """测试创建自定义有效期的许可证"""
        custom_days = 180
        license_obj = license_service.create_license(
            test_user.id,
            LicenseType.STANDARD,
            duration_days=custom_days
        )
        
        days_remaining = license_obj.days_until_expiration()
        assert 179 <= days_remaining <= 180
    
    def test_create_license_invalid_type(self, license_service, test_user):
        """测试创建无效类型的许可证"""
        with pytest.raises(LicenseError, match="无效的许可证类型"):
            license_service.create_license(test_user.id, "invalid_type")
    
    def test_create_duplicate_license(self, license_service, test_user, test_license):
        """测试为已有许可证的用户创建许可证"""
        with pytest.raises(LicenseAlreadyUsedError, match="已有许可证"):
            license_service.create_license(test_user.id, LicenseType.STANDARD)


class TestLicenseExpiration:
    """测试许可证到期检查"""
    
    def test_check_expiration_active(self, license_service, test_user, test_license):
        """测试检查活动许可证的到期时间"""
        days_remaining = license_service.check_expiration(test_user.id)
        
        # 应该接近 365 天
        assert 364 <= days_remaining <= 365
    
    def test_check_expiration_expired(self, license_service, db_session, test_user):
        """测试检查已过期许可证"""
        now = datetime.now(timezone.utc)
        expired_license = License(
            user_id=test_user.id,
            license_key="DEAD-BEEF-CAFE-BABE",
            license_type=LicenseType.TRIAL,
            status=LicenseStatus.EXPIRED,
            issued_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=10),
            max_sessions=1,
            features=["portfolio"]
        )
        db_session.add(expired_license)
        db_session.commit()
        
        days_remaining = license_service.check_expiration(test_user.id)
        
        # 应该是负数（允许一天的误差）
        assert days_remaining < 0
        assert -11 <= days_remaining <= -9
    
    def test_check_expiration_nonexistent(self, license_service, test_user):
        """测试检查不存在的许可证"""
        with pytest.raises(LicenseError, match="没有许可证"):
            license_service.check_expiration(test_user.id)


class TestLicenseRenewal:
    """测试许可证续期"""
    
    def test_renew_active_license(self, license_service, test_user, test_license):
        """测试续期活动许可证"""
        original_expires = test_license.expires_at
        
        renewed_license = license_service.renew_license(test_user.id)
        
        # 过期时间应该延长
        assert renewed_license.expires_at > original_expires
        assert renewed_license.status == LicenseStatus.ACTIVE
        
        # 应该延长约 365 天
        delta = (renewed_license.expires_at - original_expires).days
        assert 364 <= delta <= 365
    
    def test_renew_expired_license(self, license_service, db_session, test_user):
        """测试续期已过期的许可证"""
        now = datetime.now(timezone.utc)
        expired_license = License(
            user_id=test_user.id,
            license_key="DEAD-BEEF-CAFE-BABE",
            license_type=LicenseType.STANDARD,
            status=LicenseStatus.EXPIRED,
            issued_at=now - timedelta(days=400),
            expires_at=now - timedelta(days=10),
            max_sessions=3,
            features=["portfolio"]
        )
        db_session.add(expired_license)
        db_session.commit()
        
        renewed_license = license_service.renew_license(test_user.id)
        
        # 应该从现在开始计算新的过期时间
        # 确保比较时都有时区信息
        renewed_expires = renewed_license.expires_at
        if renewed_expires.tzinfo is None:
            renewed_expires = renewed_expires.replace(tzinfo=timezone.utc)
        assert renewed_expires > now
        assert renewed_license.status == LicenseStatus.ACTIVE
        
        days_remaining = renewed_license.days_until_expiration()
        assert 364 <= days_remaining <= 365
    
    def test_renew_custom_duration(self, license_service, test_user, test_license):
        """测试自定义续期时长"""
        # 记录原始过期时间
        original_expires = test_license.expires_at
        if original_expires.tzinfo is None:
            original_expires = original_expires.replace(tzinfo=timezone.utc)
        
        custom_days = 90
        renewed_license = license_service.renew_license(test_user.id, duration_days=custom_days)
        
        # 获取新的过期时间
        new_expires = renewed_license.expires_at
        if new_expires.tzinfo is None:
            new_expires = new_expires.replace(tzinfo=timezone.utc)
        
        delta = (new_expires - original_expires).days
        assert 89 <= delta <= 90


class TestLicenseSuspension:
    """测试许可证暂停和重新激活"""
    
    def test_suspend_license(self, license_service, test_user, test_license):
        """测试暂停许可证"""
        reason = "Payment overdue"
        suspended_license = license_service.suspend_license(test_user.id, reason)
        
        assert suspended_license.status == LicenseStatus.SUSPENDED
    
    def test_reactivate_license(self, license_service, test_user, test_license):
        """测试重新激活许可证"""
        # 先暂停
        license_service.suspend_license(test_user.id, "Test suspension")
        
        # 再重新激活
        reactivated_license = license_service.reactivate_license(test_user.id)
        
        assert reactivated_license.status == LicenseStatus.ACTIVE
    
    def test_reactivate_expired_license(self, license_service, db_session, test_user):
        """测试重新激活已过期的许可证"""
        now = datetime.now(timezone.utc)
        expired_license = License(
            user_id=test_user.id,
            license_key="DEAD-BEEF-CAFE-BABE",
            license_type=LicenseType.TRIAL,
            status=LicenseStatus.SUSPENDED,
            issued_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=1),
            max_sessions=1,
            features=["portfolio"]
        )
        db_session.add(expired_license)
        db_session.commit()
        
        with pytest.raises(LicenseExpiredError, match="已过期"):
            license_service.reactivate_license(test_user.id)


class TestExpirationWarnings:
    """测试到期提醒"""
    
    def test_check_expiration_warnings(self, license_service, db_session):
        """测试检查即将到期的许可证"""
        now = datetime.now(timezone.utc)
        
        # 创建几个用户和许可证
        users_and_licenses = []
        
        # 1. 5 天后到期（应该提醒）
        user1 = User(username="user1", email="user1@test.com", password_hash="hash", role="user", is_active=True)
        db_session.add(user1)
        db_session.commit()
        db_session.refresh(user1)
        
        license1 = License(
            user_id=user1.id,
            license_key="1111-1111-1111-1111",
            license_type=LicenseType.STANDARD,
            status=LicenseStatus.ACTIVE,
            issued_at=now - timedelta(days=360),
            expires_at=now + timedelta(days=5),
            max_sessions=3,
            features=["portfolio"]
        )
        db_session.add(license1)
        
        # 2. 已过期（不应该提醒）
        user2 = User(username="user2", email="user2@test.com", password_hash="hash", role="user", is_active=True)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)
        
        license2 = License(
            user_id=user2.id,
            license_key="2222-2222-2222-2222",
            license_type=LicenseType.TRIAL,
            status=LicenseStatus.EXPIRED,
            issued_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=1),
            max_sessions=1,
            features=["portfolio"]
        )
        db_session.add(license2)
        
        # 3. 还有 30 天（不应该提醒）
        user3 = User(username="user3", email="user3@test.com", password_hash="hash", role="user", is_active=True)
        db_session.add(user3)
        db_session.commit()
        db_session.refresh(user3)
        
        license3 = License(
            user_id=user3.id,
            license_key="3333-3333-3333-3333",
            license_type=LicenseType.ENTERPRISE,
            status=LicenseStatus.ACTIVE,
            issued_at=now - timedelta(days=335),
            expires_at=now + timedelta(days=30),
            max_sessions=10,
            features=["portfolio"]
        )
        db_session.add(license3)
        
        db_session.commit()
        
        # 检查提醒
        warnings = license_service.check_expiration_warnings()
        
        # 应该只有 license1 需要提醒
        assert len(warnings) == 1
        assert warnings[0]["user_id"] == user1.id
        assert 4 <= warnings[0]["days_remaining"] <= 5  # 允许一天的误差
    
    def test_no_warnings_when_all_valid(self, license_service, test_user, test_license):
        """测试所有许可证都有效时没有提醒"""
        warnings = license_service.check_expiration_warnings()
        
        # test_license 还有 365 天，不应该提醒
        assert len(warnings) == 0


class TestFeatureAccess:
    """测试功能访问权限"""
    
    def test_has_feature_access_valid(self, license_service, test_user, test_license):
        """测试有效许可证的功能访问"""
        # test_license 包含 portfolio 功能
        assert license_service.has_feature_access(test_user.id, "portfolio") is True
        assert license_service.has_feature_access(test_user.id, "market_data") is True
    
    def test_has_feature_access_invalid_feature(self, license_service, test_user, test_license):
        """测试访问许可证中不包含的功能"""
        # test_license 不包含 expert_forum 功能
        assert license_service.has_feature_access(test_user.id, "expert_forum") is False
    
    def test_has_feature_access_expired_license(self, license_service, db_session, test_user):
        """测试过期许可证的功能访问"""
        now = datetime.now(timezone.utc)
        expired_license = License(
            user_id=test_user.id,
            license_key="DEAD-BEEF-CAFE-BABE",
            license_type=LicenseType.STANDARD,
            status=LicenseStatus.EXPIRED,
            issued_at=now - timedelta(days=400),
            expires_at=now - timedelta(days=10),
            max_sessions=3,
            features=["portfolio", "market_data"]
        )
        db_session.add(expired_license)
        db_session.commit()
        
        # 过期许可证不应该有功能访问权限
        assert license_service.has_feature_access(test_user.id, "portfolio") is False
    
    def test_has_feature_access_no_license(self, license_service, test_user):
        """测试没有许可证的用户的功能访问"""
        assert license_service.has_feature_access(test_user.id, "portfolio") is False


class TestLicenseStatistics:
    """测试许可证统计"""
    
    def test_get_license_statistics(self, license_service, db_session):
        """测试获取许可证统计信息"""
        now = datetime.now(timezone.utc)
        
        # 创建多个用户和许可证
        for i in range(5):
            user = User(
                username=f"user{i}",
                email=f"user{i}@test.com",
                password_hash="hash",
                role="user",
                is_active=True
            )
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            
            # 不同类型和状态的许可证
            if i < 2:
                license_type = LicenseType.TRIAL
                status = LicenseStatus.ACTIVE
                expires_at = now + timedelta(days=30)
            elif i < 4:
                license_type = LicenseType.STANDARD
                status = LicenseStatus.ACTIVE
                expires_at = now + timedelta(days=365)
            else:
                license_type = LicenseType.ENTERPRISE
                status = LicenseStatus.EXPIRED
                expires_at = now - timedelta(days=10)
            
            license_obj = License(
                user_id=user.id,
                license_key=f"{i:04X}-{i:04X}-{i:04X}-{i:04X}",
                license_type=license_type,
                status=status,
                issued_at=now - timedelta(days=100),
                expires_at=expires_at,
                max_sessions=3,
                features=["portfolio"]
            )
            db_session.add(license_obj)
        
        db_session.commit()
        
        # 获取统计信息
        stats = license_service.get_license_statistics()
        
        assert stats["total_licenses"] == 5
        assert stats["active"] == 4
        assert stats["expired"] == 1
        assert stats["by_type"][LicenseType.TRIAL] == 2
        assert stats["by_type"][LicenseType.STANDARD] == 2
        assert stats["by_type"][LicenseType.ENTERPRISE] == 1


class TestLicenseInfo:
    """测试获取许可证信息"""
    
    def test_get_license_info(self, license_service, test_user, test_license):
        """测试获取许可证信息"""
        license_obj = license_service.get_license_info(test_user.id)
        
        assert license_obj.id == test_license.id
        assert license_obj.user_id == test_user.id
        assert license_obj.license_type == LicenseType.STANDARD
    
    def test_get_license_info_nonexistent(self, license_service, test_user):
        """测试获取不存在的许可证信息"""
        with pytest.raises(LicenseError, match="没有许可证"):
            license_service.get_license_info(test_user.id)


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_empty_features_list(self, license_service, db_session, test_user):
        """测试空功能列表的许可证"""
        license_obj = License(
            user_id=test_user.id,
            license_key="0000-0000-0000-0000",
            license_type=LicenseType.TRIAL,
            status=LicenseStatus.ACTIVE,
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            max_sessions=1,
            features=[]  # 空功能列表
        )
        db_session.add(license_obj)
        db_session.commit()
        
        # 不应该有任何功能访问权限
        assert license_service.has_feature_access(test_user.id, "portfolio") is False
    
    def test_none_features(self, license_service, db_session, test_user):
        """测试 features 为 None 的许可证"""
        license_obj = License(
            user_id=test_user.id,
            license_key="0000-0000-0000-0000",
            license_type=LicenseType.TRIAL,
            status=LicenseStatus.ACTIVE,
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            max_sessions=1,
            features=None  # None
        )
        db_session.add(license_obj)
        db_session.commit()
        
        # 不应该有任何功能访问权限
        assert license_service.has_feature_access(test_user.id, "portfolio") is False
    
    def test_license_expiring_today(self, license_service, db_session, test_user):
        """测试今天到期的许可证"""
        now = datetime.now(timezone.utc)
        # 设置为今天晚些时候到期
        expires_at = now + timedelta(hours=12)
        
        license_obj = License(
            user_id=test_user.id,
            license_key="AAAA-BBBB-CCCC-DDDD",
            license_type=LicenseType.STANDARD,
            status=LicenseStatus.ACTIVE,
            issued_at=now - timedelta(days=365),
            expires_at=expires_at,
            max_sessions=3,
            features=["portfolio"]
        )
        db_session.add(license_obj)
        db_session.commit()
        
        # 应该还是有效的
        assert license_obj.is_valid() is True
        
        # 剩余天数应该是 0
        days_remaining = license_service.check_expiration(test_user.id)
        assert days_remaining == 0
