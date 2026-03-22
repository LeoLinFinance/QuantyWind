"""
API Key 数据模型
用于存储用户自定义的大模型 API Keys
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
import uuid

from database.config import Base


class APIKey(Base):
    """
    API Key 模型
    
    存储用户配置的各种大模型服务的 API Keys
    """
    __tablename__ = "api_keys"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 用户ID（如果为空则表示系统默认配置）
    user_id = Column(String(36), nullable=True, index=True)
    
    # API Key 信息
    provider = Column(String(50), nullable=False)  # stepfun, kimi, openai 等
    api_key = Column(Text, nullable=False)  # 加密存储的 API Key
    base_url = Column(String(255), nullable=True)  # API 基础 URL（可选）
    model = Column(String(100), nullable=True)  # 默认模型（可选）
    
    # 配置名称和描述
    name = Column(String(100), nullable=True)  # 用户自定义名称
    description = Column(Text, nullable=True)  # 描述
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, provider={self.provider}, user_id={self.user_id})>"
    
    def to_dict(self, include_key=False):
        """
        转换为字典格式
        
        Args:
            include_key: 是否包含完整的 API Key（默认只显示前8位）
        
        Returns:
            dict: API Key 信息字典
        """
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_key:
            result["api_key"] = self.api_key
        else:
            # 只显示前8位和后4位
            if self.api_key and len(self.api_key) > 12:
                result["api_key_preview"] = f"{self.api_key[:8]}...{self.api_key[-4:]}"
            else:
                result["api_key_preview"] = "****"
        
        return result
