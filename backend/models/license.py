"""
License 数据模型
用于安全远程访问部署系统的许可证管理
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from database.config import Base


class License(Base):
    """
    许可证模型
    
    管理用户许可证，包括类型、状态和过期时间
    """
    __tablename__ = "licenses"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 用户关联
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # 许可证信息
    license_key = Column(String(255), unique=True, nullable=False, index=True)
    license_type = Column(String(20), nullable=False, default="trial")  # trial, standard, enterprise
    
    # 状态
    status = Column(String(20), nullable=False, default="active")  # active, expired, suspended
    
    # 时间信息
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # 限制和功能
    max_sessions = Column(Integer, default=3, nullable=False)  # 最大并发会话数
    features = Column(JSON, nullable=True)  # 可用功能列表
    
    # 创建索引以优化查询
    __table_args__ = (
        Index('idx_license_status_expires', 'status', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<License(id={self.id}, user_id={self.user_id}, type={self.license_type}, status={self.status})>"
    
    def is_expired(self):
        """
        检查许可证是否已过期
        
        Returns:
            bool: 如果许可证已过期返回 True
        """
        return datetime.now(self.expires_at.tzinfo) > self.expires_at
    
    def is_valid(self):
        """
        检查许可证是否有效
        
        Returns:
            bool: 如果许可证有效返回 True
        """
        return self.status == "active" and not self.is_expired()
    
    def days_until_expiration(self):
        """
        计算距离过期的天数
        
        Returns:
            int: 剩余天数（负数表示已过期）
        """
        delta = self.expires_at - datetime.now(self.expires_at.tzinfo)
        return delta.days
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            dict: 许可证信息字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "license_key": self.license_key,
            "license_type": self.license_type,
            "status": self.status,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "max_sessions": self.max_sessions,
            "features": self.features,
            "days_until_expiration": self.days_until_expiration()
        }
