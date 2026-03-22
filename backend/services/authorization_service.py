"""
授权服务模块
实现基于角色的访问控制（RBAC）
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.user import User


class Permission:
    """权限类"""
    def __init__(self, role: str, resource: str, actions: List[str]):
        self.role = role
        self.resource = resource
        self.actions = actions


class AuthorizationService:
    """
    授权服务
    
    负责权限检查和访问控制，实现基于角色的访问控制（RBAC）
    """
    
    # 角色权限矩阵
    # 定义每个角色对各资源的访问权限
    PERMISSIONS: Dict[str, Dict[str, List[str]]] = {
        "viewer": {
            "portfolio": ["read"],
            "market_data": ["read"],
            "risk_analysis": ["read"],
            "sentiment_map": ["read"],
            "ai_signals": ["read"],
            "expert_forum": ["read"],
            "news": ["read"]
        },
        "user": {
            "portfolio": ["read", "write"],
            "market_data": ["read", "write"],
            "risk_analysis": ["read", "write"],
            "sentiment_map": ["read", "write"],
            "ai_signals": ["read", "write"],
            "expert_forum": ["read", "write"],
            "news": ["read", "write"],
            "profile": ["read", "write"]
        },
        "admin": {
            "portfolio": ["read", "write", "delete"],
            "market_data": ["read", "write", "delete"],
            "risk_analysis": ["read", "write", "delete"],
            "sentiment_map": ["read", "write", "delete"],
            "ai_signals": ["read", "write", "delete"],
            "expert_forum": ["read", "write", "delete"],
            "news": ["read", "write", "delete"],
            "profile": ["read", "write", "delete"],
            "user_management": ["read", "write", "delete"],
            "system_config": ["read", "write", "delete"],
            "audit_logs": ["read"],
            "license_management": ["read", "write"]
        }
    }
    
    # 有效的角色列表
    VALID_ROLES = ["viewer", "user", "admin"]
    
    def __init__(self, db: Session):
        """
        初始化授权服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """
        检查用户是否有权限执行特定操作
        
        Args:
            user_id: 用户 ID
            resource: 资源标识符（如 "portfolio", "market_data"）
            action: 操作类型（如 "read", "write", "delete"）
        
        Returns:
            bool: 是否有权限
        """
        # 获取用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 检查账户状态
        if not user.is_active or user.is_locked:
            return False
        
        # 获取用户角色的权限
        role_permissions = self.PERMISSIONS.get(user.role, {})
        resource_permissions = role_permissions.get(resource, [])
        
        # 检查是否有该操作的权限
        return action in resource_permissions
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """
        获取用户的所有权限
        
        Args:
            user_id: 用户 ID
        
        Returns:
            List[Permission]: 权限列表
        """
        # 获取用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 获取用户角色的所有权限
        role_permissions = self.PERMISSIONS.get(user.role, {})
        
        # 转换为 Permission 对象列表
        permissions = []
        for resource, actions in role_permissions.items():
            permissions.append(Permission(user.role, resource, actions))
        
        return permissions
    
    def assign_role(self, user_id: str, role: str) -> bool:
        """
        为用户分配角色
        
        Args:
            user_id: 用户 ID
            role: 角色名称（viewer, user, admin）
        
        Returns:
            bool: 分配是否成功
        
        Raises:
            ValueError: 角色不存在
        """
        # 验证角色是否有效
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {role}. Valid roles are: {', '.join(self.VALID_ROLES)}")
        
        # 获取用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 更新角色
        user.role = role
        self.db.commit()
        
        return True
    
    def update_role(self, user_id: str, new_role: str) -> bool:
        """
        更新用户角色
        
        Args:
            user_id: 用户 ID
            new_role: 新角色名称
        
        Returns:
            bool: 更新是否成功
        
        Raises:
            ValueError: 角色不存在
        """
        return self.assign_role(user_id, new_role)
    
    def get_user_role(self, user_id: str) -> Optional[str]:
        """
        获取用户角色
        
        Args:
            user_id: 用户 ID
        
        Returns:
            Optional[str]: 用户角色，如果用户不存在则返回 None
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return user.role
    
    def has_role(self, user_id: str, role: str) -> bool:
        """
        检查用户是否具有指定角色
        
        Args:
            user_id: 用户 ID
            role: 角色名称
        
        Returns:
            bool: 是否具有该角色
        """
        user_role = self.get_user_role(user_id)
        return user_role == role
    
    def is_admin(self, user_id: str) -> bool:
        """
        检查用户是否是管理员
        
        Args:
            user_id: 用户 ID
        
        Returns:
            bool: 是否是管理员
        """
        return self.has_role(user_id, "admin")
    
    def get_resource_permissions(self, user_id: str, resource: str) -> List[str]:
        """
        获取用户对特定资源的权限列表
        
        Args:
            user_id: 用户 ID
            resource: 资源标识符
        
        Returns:
            List[str]: 该资源的操作权限列表
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        role_permissions = self.PERMISSIONS.get(user.role, {})
        return role_permissions.get(resource, [])
    
    @classmethod
    def get_all_resources(cls) -> List[str]:
        """
        获取所有可用资源列表
        
        Returns:
            List[str]: 资源列表
        """
        resources = set()
        for role_perms in cls.PERMISSIONS.values():
            resources.update(role_perms.keys())
        return sorted(list(resources))
    
    @classmethod
    def get_role_permissions_matrix(cls) -> Dict[str, Dict[str, List[str]]]:
        """
        获取完整的角色权限矩阵
        
        Returns:
            Dict[str, Dict[str, List[str]]]: 角色权限矩阵
        """
        return cls.PERMISSIONS.copy()
