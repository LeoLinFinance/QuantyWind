"""
API Key 管理服务
提供 API Key 的增删改查和加密存储功能
"""
import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.api_key import APIKey
from services.encryption_service import EncryptionService

logger = logging.getLogger(__name__)


class APIKeyService:
    """API Key 管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption_service = EncryptionService()
    
    def create_api_key(
        self,
        provider: str,
        api_key: str,
        user_id: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> APIKey:
        """
        创建新的 API Key
        
        Args:
            provider: 服务提供商（stepfun, kimi, openai 等）
            api_key: API Key（将被加密存储）
            user_id: 用户ID（可选，为空表示系统默认）
            base_url: API 基础 URL（可选）
            model: 默认模型（可选）
            name: 自定义名称（可选）
            description: 描述（可选）
        
        Returns:
            创建的 APIKey 对象
        """
        try:
            # 加密 API Key
            encrypted_key = self.encryption_service.encrypt(api_key)
            
            # 创建记录
            db_api_key = APIKey(
                user_id=user_id,
                provider=provider,
                api_key=encrypted_key,
                base_url=base_url,
                model=model,
                name=name,
                description=description
            )
            
            self.db.add(db_api_key)
            self.db.commit()
            self.db.refresh(db_api_key)
            
            logger.info(f"Created API key for provider: {provider}, user: {user_id or 'system'}")
            return db_api_key
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create API key: {e}")
            raise
    
    def get_api_key(self, key_id: str) -> Optional[APIKey]:
        """
        获取指定的 API Key
        
        Args:
            key_id: API Key ID
        
        Returns:
            APIKey 对象或 None
        """
        return self.db.query(APIKey).filter(APIKey.id == key_id).first()
    
    def get_user_api_keys(self, user_id: Optional[str] = None, provider: Optional[str] = None) -> List[APIKey]:
        """
        获取用户的所有 API Keys
        
        Args:
            user_id: 用户ID（None 表示获取系统默认配置）
            provider: 过滤特定提供商（可选）
        
        Returns:
            APIKey 对象列表
        """
        query = self.db.query(APIKey).filter(APIKey.user_id == user_id)
        
        if provider:
            query = query.filter(APIKey.provider == provider)
        
        return query.filter(APIKey.is_active == True).all()
    
    def get_active_api_key(self, provider: str, user_id: Optional[str] = None) -> Optional[str]:
        """
        获取解密后的活跃 API Key
        
        优先返回用户配置的 Key，如果没有则返回系统默认 Key
        
        Args:
            provider: 服务提供商
            user_id: 用户ID（可选）
        
        Returns:
            解密后的 API Key 字符串或 None
        """
        # 先查找用户配置
        if user_id:
            user_key = self.db.query(APIKey).filter(
                and_(
                    APIKey.user_id == user_id,
                    APIKey.provider == provider,
                    APIKey.is_active == True
                )
            ).first()
            
            if user_key:
                try:
                    return self.encryption_service.decrypt(user_key.api_key)
                except Exception as e:
                    logger.error(f"Failed to decrypt user API key: {e}")
        
        # 查找系统默认配置
        system_key = self.db.query(APIKey).filter(
            and_(
                APIKey.user_id == None,
                APIKey.provider == provider,
                APIKey.is_active == True
            )
        ).first()
        
        if system_key:
            try:
                return self.encryption_service.decrypt(system_key.api_key)
            except Exception as e:
                logger.error(f"Failed to decrypt system API key: {e}")
        
        return None
    
    def update_api_key(
        self,
        key_id: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[APIKey]:
        """
        更新 API Key
        
        Args:
            key_id: API Key ID
            api_key: 新的 API Key（可选，将被加密）
            base_url: 新的基础 URL（可选）
            model: 新的默认模型（可选）
            name: 新的名称（可选）
            description: 新的描述（可选）
            is_active: 新的状态（可选）
        
        Returns:
            更新后的 APIKey 对象或 None
        """
        try:
            db_api_key = self.get_api_key(key_id)
            if not db_api_key:
                return None
            
            if api_key is not None:
                db_api_key.api_key = self.encryption_service.encrypt(api_key)
            if base_url is not None:
                db_api_key.base_url = base_url
            if model is not None:
                db_api_key.model = model
            if name is not None:
                db_api_key.name = name
            if description is not None:
                db_api_key.description = description
            if is_active is not None:
                db_api_key.is_active = is_active
            
            self.db.commit()
            self.db.refresh(db_api_key)
            
            logger.info(f"Updated API key: {key_id}")
            return db_api_key
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update API key: {e}")
            raise
    
    def delete_api_key(self, key_id: str) -> bool:
        """
        删除 API Key
        
        Args:
            key_id: API Key ID
        
        Returns:
            是否删除成功
        """
        try:
            db_api_key = self.get_api_key(key_id)
            if not db_api_key:
                return False
            
            self.db.delete(db_api_key)
            self.db.commit()
            
            logger.info(f"Deleted API key: {key_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete API key: {e}")
            raise
