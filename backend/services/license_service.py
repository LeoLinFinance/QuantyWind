"""
许可证管理服务模块

提供许可证管理功能：
- 许可证验证
- 许可证激活
- 许可证到期检查
- 许可证使用记录
- 到期提醒功能

需求：12.1, 12.2, 12.3, 12.4, 12.5
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.license import License
from models.user import User
from services.audit_log_service import AuditLogService


class LicenseError(Exception):
    """许可证相关错误的基类"""
    pass


class InvalidLicenseKeyError(LicenseError):
    """许可证密钥无效异常"""
    pass


class LicenseAlreadyUsedError(LicenseError):
    """许可证已被使用异常"""
    pass


class LicenseExpiredError(LicenseError):
    """许可证已过期异常"""
    pass


class LicenseSuspendedError(LicenseError):
    """许可证已暂停异常"""
    pass


class LicenseStatus:
    """许可证状态枚举"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class LicenseType:
    """许可证类型枚举"""
    TRIAL = "trial"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"


class LicenseService:
    """
    许可证管理服务
    
    负责管理用户许可证的完整生命周期，包括：
    - 验证许可证有效性
    - 激活新许可证
    - 检查许可证到期时间
    - 记录许可证使用情况
    - 发送到期提醒
    """
    
    # 许可证配置
    LICENSE_KEY_LENGTH = 32  # 许可证密钥长度
    EXPIRATION_WARNING_DAYS = 7  # 到期提醒天数
    
    # 不同类型许可证的默认配置
    LICENSE_CONFIGS = {
        LicenseType.TRIAL: {
            "duration_days": 30,
            "max_sessions": 1,
            "features": ["portfolio", "market_data", "risk_analysis"]
        },
        LicenseType.STANDARD: {
            "duration_days": 365,
            "max_sessions": 3,
            "features": [
                "portfolio", "market_data", "risk_analysis",
                "sentiment_map", "ai_signals", "news"
            ]
        },
        LicenseType.ENTERPRISE: {
            "duration_days": 365,
            "max_sessions": 10,
            "features": [
                "portfolio", "market_data", "risk_analysis",
                "sentiment_map", "ai_signals", "news",
                "expert_forum", "advanced_analytics", "api_access"
            ]
        }
    }
    
    def __init__(self, db: Session):
        """
        初始化许可证服务
        
        参数:
            db: 数据库会话
        """
        self.db = db
        self.audit_service = AuditLogService(db)
    
    def _generate_license_key(self) -> str:
        """
        生成唯一的许可证密钥
        
        返回:
            str: 许可证密钥（格式：XXXX-XXXX-XXXX-XXXX）
        """
        # 生成随机字节
        random_bytes = secrets.token_bytes(self.LICENSE_KEY_LENGTH // 2)
        
        # 转换为十六进制字符串
        hex_string = random_bytes.hex().upper()
        
        # 格式化为 XXXX-XXXX-XXXX-XXXX 格式
        parts = [hex_string[i:i+4] for i in range(0, len(hex_string), 4)]
        license_key = "-".join(parts[:4])
        
        return license_key
    
    def _validate_license_key_format(self, license_key: str) -> bool:
        """
        验证许可证密钥格式
        
        参数:
            license_key: 许可证密钥
        
        返回:
            bool: 格式是否有效
        """
        # 检查格式：XXXX-XXXX-XXXX-XXXX（支持字母和数字）
        parts = license_key.split("-")
        if len(parts) != 4:
            return False
        
        for part in parts:
            if len(part) != 4 or not all(c.isalnum() for c in part):
                return False
        
        return True
    
    def validate_license(self, user_id: str) -> str:
        """
        验证用户许可证
        
        参数:
            user_id: 用户 ID
        
        返回:
            str: 许可证状态（active, expired, suspended）
        
        异常:
            LicenseError: 许可证不存在
        """
        # 查找用户的许可证
        license_obj = self.db.query(License).filter(
            License.user_id == user_id
        ).first()
        
        if not license_obj:
            raise LicenseError(f"用户 {user_id} 没有许可证")
        
        # 检查是否过期
        if license_obj.is_expired():
            # 更新状态为过期
            if license_obj.status != LicenseStatus.EXPIRED:
                license_obj.status = LicenseStatus.EXPIRED
                self.db.commit()
                
                # 记录安全事件
                self.audit_service.log_security_event(
                    event_type="license_expired",
                    severity="medium",
                    description=f"License expired for user {user_id}",
                    metadata={
                        "license_id": license_obj.id,
                        "license_type": license_obj.license_type,
                        "expired_at": license_obj.expires_at.isoformat()
                    },
                    user_id=user_id
                )
            
            return LicenseStatus.EXPIRED
        
        # 记录许可证使用
        self._record_license_usage(user_id, "validate")
        
        return license_obj.status
    
    def get_license_info(self, user_id: str) -> License:
        """
        获取许可证信息
        
        参数:
            user_id: 用户 ID
        
        返回:
            License: 许可证详情
        
        异常:
            LicenseError: 许可证不存在
        """
        license_obj = self.db.query(License).filter(
            License.user_id == user_id
        ).first()
        
        if not license_obj:
            raise LicenseError(f"用户 {user_id} 没有许可证")
        
        return license_obj
    
    def check_expiration(self, user_id: str) -> int:
        """
        检查许可证到期时间
        
        参数:
            user_id: 用户 ID
        
        返回:
            int: 剩余天数（负数表示已过期）
        
        异常:
            LicenseError: 许可证不存在
        """
        license_obj = self.get_license_info(user_id)
        return license_obj.days_until_expiration()
    
    def activate_license(
        self,
        user_id: str,
        license_key: str
    ) -> License:
        """
        激活许可证
        
        参数:
            user_id: 用户 ID
            license_key: 许可证密钥
        
        返回:
            License: 激活的许可证对象
        
        异常:
            InvalidLicenseKeyError: 许可证密钥无效
            LicenseAlreadyUsedError: 许可证已被使用
        """
        # 验证密钥格式
        if not self._validate_license_key_format(license_key):
            raise InvalidLicenseKeyError("许可证密钥格式无效")
        
        # 检查用户是否存在
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise LicenseError(f"用户 {user_id} 不存在")
        
        # 检查用户是否已有许可证
        existing_license = self.db.query(License).filter(
            License.user_id == user_id
        ).first()
        
        if existing_license:
            raise LicenseAlreadyUsedError(f"用户 {user_id} 已有许可证")
        
        # 检查许可证密钥是否已被使用
        used_license = self.db.query(License).filter(
            License.license_key == license_key
        ).first()
        
        if used_license:
            raise LicenseAlreadyUsedError(f"许可证密钥 {license_key} 已被使用")
        
        # 从密钥推断许可证类型（这里简化处理，实际应该有更复杂的验证逻辑）
        # 在实际应用中，应该有一个预生成的许可证密钥数据库
        license_type = LicenseType.STANDARD  # 默认为标准版
        
        # 创建许可证
        license_obj = self._create_license(user_id, license_type, license_key)
        
        # 记录激活事件
        self.audit_service.log_security_event(
            event_type="license_activated",
            severity="info",
            description=f"License activated for user {user_id}",
            metadata={
                "license_id": license_obj.id,
                "license_type": license_obj.license_type,
                "license_key": license_key,
                "expires_at": license_obj.expires_at.isoformat()
            },
            user_id=user_id
        )
        
        return license_obj
    
    def create_license(
        self,
        user_id: str,
        license_type: str,
        duration_days: Optional[int] = None
    ) -> License:
        """
        创建新许可证（管理员功能）
        
        参数:
            user_id: 用户 ID
            license_type: 许可证类型（trial, standard, enterprise）
            duration_days: 有效期天数（可选，默认使用类型配置）
        
        返回:
            License: 创建的许可证对象
        
        异常:
            LicenseError: 用户已有许可证或类型无效
        """
        # 验证许可证类型
        if license_type not in self.LICENSE_CONFIGS:
            raise LicenseError(f"无效的许可证类型: {license_type}")
        
        # 检查用户是否已有许可证
        existing_license = self.db.query(License).filter(
            License.user_id == user_id
        ).first()
        
        if existing_license:
            raise LicenseAlreadyUsedError(f"用户 {user_id} 已有许可证")
        
        # 生成唯一的许可证密钥
        license_key = self._generate_license_key()
        while self.db.query(License).filter(License.license_key == license_key).first():
            license_key = self._generate_license_key()
        
        # 创建许可证
        return self._create_license(user_id, license_type, license_key, duration_days)
    
    def _create_license(
        self,
        user_id: str,
        license_type: str,
        license_key: str,
        duration_days: Optional[int] = None
    ) -> License:
        """
        内部方法：创建许可证对象
        
        参数:
            user_id: 用户 ID
            license_type: 许可证类型
            license_key: 许可证密钥
            duration_days: 有效期天数（可选）
        
        返回:
            License: 创建的许可证对象
        """
        config = self.LICENSE_CONFIGS[license_type]
        
        # 计算过期时间
        now = datetime.now(timezone.utc)
        days = duration_days if duration_days is not None else config["duration_days"]
        expires_at = now + timedelta(days=days)
        
        # 创建许可证对象
        license_obj = License(
            user_id=user_id,
            license_key=license_key,
            license_type=license_type,
            status=LicenseStatus.ACTIVE,
            issued_at=now,
            expires_at=expires_at,
            max_sessions=config["max_sessions"],
            features=config["features"]
        )
        
        self.db.add(license_obj)
        self.db.commit()
        self.db.refresh(license_obj)
        
        return license_obj
    
    def renew_license(
        self,
        user_id: str,
        duration_days: Optional[int] = None
    ) -> License:
        """
        续期许可证
        
        参数:
            user_id: 用户 ID
            duration_days: 续期天数（可选，默认使用类型配置）
        
        返回:
            License: 更新后的许可证对象
        
        异常:
            LicenseError: 许可证不存在
        """
        license_obj = self.get_license_info(user_id)
        
        # 获取配置
        config = self.LICENSE_CONFIGS.get(license_obj.license_type, {})
        days = duration_days if duration_days is not None else config.get("duration_days", 365)
        
        # 从当前时间或过期时间（如果未过期）开始计算
        now = datetime.now(timezone.utc)
        # 确保 expires_at 有时区信息
        expires_at = license_obj.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at > now:
            # 未过期，从过期时间开始续期
            new_expires_at = expires_at + timedelta(days=days)
        else:
            # 已过期，从现在开始续期
            new_expires_at = now + timedelta(days=days)
        
        # 更新许可证
        license_obj.expires_at = new_expires_at
        license_obj.status = LicenseStatus.ACTIVE
        self.db.commit()
        self.db.refresh(license_obj)
        
        # 记录续期事件
        self.audit_service.log_security_event(
            event_type="license_renewed",
            severity="info",
            description=f"License renewed for user {user_id}",
            metadata={
                "license_id": license_obj.id,
                "license_type": license_obj.license_type,
                "new_expires_at": new_expires_at.isoformat(),
                "duration_days": days
            },
            user_id=user_id
        )
        
        return license_obj
    
    def suspend_license(self, user_id: str, reason: str) -> License:
        """
        暂停许可证
        
        参数:
            user_id: 用户 ID
            reason: 暂停原因
        
        返回:
            License: 更新后的许可证对象
        
        异常:
            LicenseError: 许可证不存在
        """
        license_obj = self.get_license_info(user_id)
        
        license_obj.status = LicenseStatus.SUSPENDED
        self.db.commit()
        
        # 记录暂停事件
        self.audit_service.log_security_event(
            event_type="license_suspended",
            severity="high",
            description=f"License suspended for user {user_id}",
            metadata={
                "license_id": license_obj.id,
                "license_type": license_obj.license_type,
                "reason": reason
            },
            user_id=user_id
        )
        
        return license_obj
    
    def reactivate_license(self, user_id: str) -> License:
        """
        重新激活许可证
        
        参数:
            user_id: 用户 ID
        
        返回:
            License: 更新后的许可证对象
        
        异常:
            LicenseError: 许可证不存在或已过期
        """
        license_obj = self.get_license_info(user_id)
        
        # 检查是否过期
        if license_obj.is_expired():
            raise LicenseExpiredError("无法重新激活已过期的许可证，请先续期")
        
        license_obj.status = LicenseStatus.ACTIVE
        self.db.commit()
        
        # 记录重新激活事件
        self.audit_service.log_security_event(
            event_type="license_reactivated",
            severity="info",
            description=f"License reactivated for user {user_id}",
            metadata={
                "license_id": license_obj.id,
                "license_type": license_obj.license_type
            },
            user_id=user_id
        )
        
        return license_obj
    
    def _record_license_usage(
        self,
        user_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        记录许可证使用情况
        
        参数:
            user_id: 用户 ID
            action: 操作类型（validate, login, feature_access）
            metadata: 额外元数据
        """
        try:
            license_obj = self.get_license_info(user_id)
            
            details = metadata or {}
            details.update({
                "license_id": license_obj.id,
                "license_type": license_obj.license_type,
                "action": action
            })
            
            # 使用审计日志记录使用情况
            self.audit_service.log_security_event(
                event_type="license_usage",
                severity="info",
                description=f"License usage: {action}",
                metadata=details,
                user_id=user_id
            )
        except LicenseError:
            # 如果许可证不存在，忽略记录
            pass
    
    def check_expiration_warnings(self) -> List[Dict[str, Any]]:
        """
        检查需要发送到期提醒的许可证
        
        返回:
            List[Dict[str, Any]]: 需要提醒的许可证列表
        """
        now = datetime.now(timezone.utc)
        warning_date = now + timedelta(days=self.EXPIRATION_WARNING_DAYS)
        
        # 查询即将到期的活动许可证
        expiring_licenses = self.db.query(License).filter(
            and_(
                License.status == LicenseStatus.ACTIVE,
                License.expires_at <= warning_date,
                License.expires_at > now
            )
        ).all()
        
        warnings = []
        for license_obj in expiring_licenses:
            days_remaining = license_obj.days_until_expiration()
            
            warnings.append({
                "user_id": license_obj.user_id,
                "license_id": license_obj.id,
                "license_type": license_obj.license_type,
                "expires_at": license_obj.expires_at.isoformat(),
                "days_remaining": days_remaining
            })
            
            # 记录提醒事件
            self.audit_service.log_security_event(
                event_type="license_expiration_warning",
                severity="medium",
                description=f"License expiring in {days_remaining} days",
                metadata={
                    "license_id": license_obj.id,
                    "license_type": license_obj.license_type,
                    "expires_at": license_obj.expires_at.isoformat(),
                    "days_remaining": days_remaining
                },
                user_id=license_obj.user_id
            )
        
        return warnings
    
    def get_license_statistics(self) -> Dict[str, Any]:
        """
        获取许可证统计信息
        
        返回:
            Dict[str, Any]: 统计信息
        """
        total_licenses = self.db.query(License).count()
        
        # 按状态统计
        active_count = self.db.query(License).filter(
            License.status == LicenseStatus.ACTIVE
        ).count()
        
        expired_count = self.db.query(License).filter(
            License.status == LicenseStatus.EXPIRED
        ).count()
        
        suspended_count = self.db.query(License).filter(
            License.status == LicenseStatus.SUSPENDED
        ).count()
        
        # 按类型统计
        by_type = {}
        for license_type in [LicenseType.TRIAL, LicenseType.STANDARD, LicenseType.ENTERPRISE]:
            count = self.db.query(License).filter(
                License.license_type == license_type
            ).count()
            by_type[license_type] = count
        
        # 即将到期的许可证数量
        now = datetime.now(timezone.utc)
        warning_date = now + timedelta(days=self.EXPIRATION_WARNING_DAYS)
        expiring_soon = self.db.query(License).filter(
            and_(
                License.status == LicenseStatus.ACTIVE,
                License.expires_at <= warning_date,
                License.expires_at > now
            )
        ).count()
        
        return {
            "total_licenses": total_licenses,
            "active": active_count,
            "expired": expired_count,
            "suspended": suspended_count,
            "by_type": by_type,
            "expiring_soon": expiring_soon
        }
    
    def has_feature_access(self, user_id: str, feature: str) -> bool:
        """
        检查用户是否有权访问特定功能
        
        参数:
            user_id: 用户 ID
            feature: 功能名称
        
        返回:
            bool: 是否有权访问
        """
        try:
            license_obj = self.get_license_info(user_id)
            
            # 检查许可证是否有效
            if not license_obj.is_valid():
                return False
            
            # 检查功能是否在许可证中
            if license_obj.features and feature in license_obj.features:
                # 记录功能访问
                self._record_license_usage(
                    user_id,
                    "feature_access",
                    {"feature": feature}
                )
                return True
            
            return False
        except LicenseError:
            return False


def get_license_service(db: Session) -> LicenseService:
    """
    获取许可证服务实例
    用于依赖注入
    
    参数:
        db: 数据库会话
    
    返回:
        LicenseService: 许可证服务实例
    """
    return LicenseService(db)
