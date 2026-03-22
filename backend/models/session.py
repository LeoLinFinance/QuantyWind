"""
Session 数据模型
用于安全远程访问部署系统的会话管理
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from database.config import Base


class Session(Base):
    """
    会话模型
    
    存储用户会话信息，包括令牌、IP 地址和过期时间
    """
    __tablename__ = "sessions"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 用户关联
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 会话信息
    token = Column(String(512), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # 支持 IPv6
    user_agent = Column(String(512), nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
    
    def is_expired(self):
        """
        检查会话是否已过期
        
        Returns:
            bool: 如果会话已过期返回 True
        """
        return datetime.now(self.expires_at.tzinfo) > self.expires_at
    
    def is_valid(self):
        """
        检查会话是否有效
        
        Returns:
            bool: 如果会话有效返回 True
        """
        return self.is_active and not self.is_expired()
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            dict: 会话信息字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
