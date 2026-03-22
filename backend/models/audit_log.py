"""
AuditLog 数据模型
用于安全远程访问部署系统的审计日志记录
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Index
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from database.config import Base


class AuditLog(Base):
    """
    审计日志模型
    
    记录所有安全相关事件，包括身份验证、授权和系统操作
    """
    __tablename__ = "audit_logs"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 事件信息
    event_type = Column(String(50), nullable=False, index=True)  # authentication, authorization, security_event, etc.
    action = Column(String(100), nullable=False)  # login, logout, permission_check, etc.
    
    # 用户和资源
    user_id = Column(String(36), nullable=True, index=True)  # 可选，某些事件可能没有用户
    resource = Column(String(255), nullable=True)  # 操作的资源
    
    # 网络信息
    ip_address = Column(String(45), nullable=True)
    
    # 结果
    success = Column(Boolean, nullable=False)
    
    # 严重程度
    severity = Column(String(20), nullable=False, default="info")  # low, medium, high, critical
    
    # 详细信息
    details = Column(JSON, nullable=True)  # 存储额外的上下文信息
    
    # 时间戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # 创建复合索引以优化查询
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_event_timestamp', 'event_type', 'timestamp'),
        Index('idx_audit_severity_timestamp', 'severity', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type={self.event_type}, action={self.action}, success={self.success})>"
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            dict: 审计日志信息字典
        """
        return {
            "id": self.id,
            "event_type": self.event_type,
            "action": self.action,
            "user_id": self.user_id,
            "resource": self.resource,
            "ip_address": self.ip_address,
            "success": self.success,
            "severity": self.severity,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
