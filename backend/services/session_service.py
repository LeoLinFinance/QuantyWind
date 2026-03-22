"""
会话管理服务
负责管理用户会话生命周期，包括创建、验证、更新和终止会话
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from redis import Redis

from database.config import get_redis_client


class SessionError(Exception):
    """会话相关错误的基类"""
    pass


class SessionExpiredError(SessionError):
    """会话已过期错误"""
    pass


class SessionAnomalyError(SessionError):
    """会话异常错误（如 IP 地址变化）"""
    pass


class MaxSessionsExceededError(SessionError):
    """超过最大会话数错误"""
    pass


class Session:
    """
    会话对象
    
    Attributes:
        id: 会话唯一标识符
        user_id: 用户 ID
        token: 会话令牌
        ip_address: 客户端 IP 地址
        user_agent: 客户端 User-Agent
        created_at: 创建时间
        last_activity: 最后活动时间
        expires_at: 过期时间
        is_active: 是否活动
    """
    
    def __init__(
        self,
        id: str,
        user_id: str,
        token: str,
        ip_address: str,
        user_agent: str,
        created_at: datetime,
        last_activity: datetime,
        expires_at: datetime,
        is_active: bool = True
    ):
        self.id = id
        self.user_id = user_id
        self.token = token
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at
        self.last_activity = last_activity
        self.expires_at = expires_at
        self.is_active = is_active
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """从字典创建会话对象"""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            token=data["token"],
            ip_address=data["ip_address"],
            user_agent=data["user_agent"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            is_active=data.get("is_active", True)
        )


class SessionService:
    """
    会话管理服务
    
    负责管理用户会话的完整生命周期，包括：
    - 创建新会话
    - 验证会话有效性
    - 更新会话活动时间
    - 终止会话
    - 管理单用户多会话限制
    """
    
    # 会话配置常量
    SESSION_TIMEOUT_MINUTES = 30  # 会话超时时间（分钟）
    MAX_SESSIONS_PER_USER = 3     # 每个用户最大并发会话数
    
    # Redis 键前缀
    SESSION_KEY_PREFIX = "session:"
    USER_SESSIONS_KEY_PREFIX = "user_sessions:"
    
    def __init__(self, redis_client: Optional[Redis] = None):
        """
        初始化会话服务
        
        Args:
            redis_client: Redis 客户端实例（可选，默认使用全局客户端）
        """
        self.redis = redis_client or get_redis_client()
    
    def _get_session_key(self, session_id: str) -> str:
        """获取会话的 Redis 键"""
        return f"{self.SESSION_KEY_PREFIX}{session_id}"
    
    def _get_user_sessions_key(self, user_id: str) -> str:
        """获取用户会话列表的 Redis 键"""
        return f"{self.USER_SESSIONS_KEY_PREFIX}{user_id}"
    
    def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str
    ) -> Session:
        """
        创建新会话
        
        Args:
            user_id: 用户 ID
            ip_address: 客户端 IP 地址
            user_agent: 客户端 User-Agent
        
        Returns:
            Session: 创建的会话对象
        
        Raises:
            MaxSessionsExceededError: 超过最大会话数限制
        """
        # 检查用户当前活动会话数
        active_sessions = self.get_active_sessions(user_id)
        if len(active_sessions) >= self.MAX_SESSIONS_PER_USER:
            # 删除最旧的会话以腾出空间
            oldest_session = min(active_sessions, key=lambda s: s.created_at)
            self.terminate_session(oldest_session.id)
        
        # 生成会话 ID 和令牌
        session_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        
        # 创建会话对象
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        
        session = Session(
            id=session_id,
            user_id=user_id,
            token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            is_active=True
        )
        
        # 存储会话到 Redis
        session_key = self._get_session_key(session_id)
        session_data = json.dumps(session.to_dict())
        
        # 设置会话数据，并设置过期时间
        ttl_seconds = int(self.SESSION_TIMEOUT_MINUTES * 60)
        self.redis.setex(session_key, ttl_seconds, session_data)
        
        # 将会话 ID 添加到用户会话列表
        user_sessions_key = self._get_user_sessions_key(user_id)
        self.redis.sadd(user_sessions_key, session_id)
        
        return session
    
    def validate_session(
        self,
        session_id: str,
        ip_address: str
    ) -> bool:
        """
        验证会话有效性
        
        Args:
            session_id: 会话 ID
            ip_address: 当前请求的 IP 地址
        
        Returns:
            bool: 会话是否有效
        
        Raises:
            SessionExpiredError: 会话已过期
            SessionAnomalyError: 检测到会话异常（如 IP 变化）
        """
        # 获取会话数据
        session = self._get_session(session_id)
        
        if session is None:
            raise SessionExpiredError(f"Session {session_id} not found or expired")
        
        # 检查会话是否活动
        if not session.is_active:
            raise SessionExpiredError(f"Session {session_id} is not active")
        
        # 检查会话是否过期
        if datetime.utcnow() > session.expires_at:
            self.terminate_session(session_id)
            raise SessionExpiredError(f"Session {session_id} has expired")
        
        # 检查 IP 地址是否一致（安全检查）
        if session.ip_address != ip_address:
            # IP 地址变化，终止会话并抛出异常
            self.terminate_session(session_id)
            raise SessionAnomalyError(
                f"IP address mismatch for session {session_id}. "
                f"Expected: {session.ip_address}, Got: {ip_address}"
            )
        
        return True
    
    def update_activity(self, session_id: str) -> bool:
        """
        更新会话最后活动时间
        
        Args:
            session_id: 会话 ID
        
        Returns:
            bool: 更新是否成功
        """
        session = self._get_session(session_id)
        
        if session is None:
            return False
        
        # 更新最后活动时间和过期时间
        now = datetime.utcnow()
        session.last_activity = now
        session.expires_at = now + timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        
        # 保存更新后的会话
        session_key = self._get_session_key(session_id)
        session_data = json.dumps(session.to_dict())
        ttl_seconds = int(self.SESSION_TIMEOUT_MINUTES * 60)
        self.redis.setex(session_key, ttl_seconds, session_data)
        
        return True
    
    def terminate_session(self, session_id: str) -> bool:
        """
        终止会话
        
        Args:
            session_id: 会话 ID
        
        Returns:
            bool: 终止是否成功
        """
        # 获取会话以获取用户 ID
        session = self._get_session(session_id)
        
        if session is None:
            return False
        
        # 从 Redis 删除会话数据
        session_key = self._get_session_key(session_id)
        self.redis.delete(session_key)
        
        # 从用户会话列表中移除
        user_sessions_key = self._get_user_sessions_key(session.user_id)
        self.redis.srem(user_sessions_key, session_id)
        
        return True
    
    def get_active_sessions(self, user_id: str) -> List[Session]:
        """
        获取用户的所有活动会话
        
        Args:
            user_id: 用户 ID
        
        Returns:
            List[Session]: 活动会话列表
        """
        user_sessions_key = self._get_user_sessions_key(user_id)
        session_ids = self.redis.smembers(user_sessions_key)
        
        active_sessions = []
        for session_id in session_ids:
            session = self._get_session(session_id)
            if session is not None and session.is_active:
                # 检查是否过期
                if datetime.utcnow() <= session.expires_at:
                    active_sessions.append(session)
                else:
                    # 清理过期会话
                    self.terminate_session(session_id)
        
        return active_sessions
    
    def terminate_all_user_sessions(self, user_id: str) -> int:
        """
        终止用户的所有会话
        
        Args:
            user_id: 用户 ID
        
        Returns:
            int: 终止的会话数量
        """
        sessions = self.get_active_sessions(user_id)
        count = 0
        
        for session in sessions:
            if self.terminate_session(session.id):
                count += 1
        
        return count
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取会话信息（公开方法）
        
        Args:
            session_id: 会话 ID
        
        Returns:
            Optional[Session]: 会话对象，如果不存在则返回 None
        """
        return self._get_session(session_id)
    
    def _get_session(self, session_id: str) -> Optional[Session]:
        """
        从 Redis 获取会话数据（内部方法）
        
        Args:
            session_id: 会话 ID
        
        Returns:
            Optional[Session]: 会话对象，如果不存在则返回 None
        """
        session_key = self._get_session_key(session_id)
        session_data = self.redis.get(session_key)
        
        if session_data is None:
            return None
        
        try:
            data = json.loads(session_data)
            return Session.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            # 数据损坏，删除会话
            self.redis.delete(session_key)
            return None


# 全局会话服务实例
_session_service: Optional[SessionService] = None


def get_session_service() -> SessionService:
    """
    获取会话服务实例（单例模式）
    
    Returns:
        SessionService: 会话服务实例
    """
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
