"""
身份验证服务模块

提供用户身份验证和授权管理功能：
- 用户注册（包含密码强度验证）
- 用户登录（生成 JWT 令牌）
- 令牌验证和刷新
- 令牌撤销（使用 Redis 黑名单）
- 账户锁定机制（5 次失败后锁定 15 分钟）

需求：2.1, 2.2, 2.3, 2.4
"""

import os
import re
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from models.user import User
from services.encryption_service import get_encryption_service
from database.config import get_redis_client


class AuthenticationError(Exception):
    """身份验证异常基类"""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """用户已存在异常"""
    pass


class WeakPasswordError(AuthenticationError):
    """密码强度不足异常"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """凭证无效异常"""
    pass


class AccountLockedError(AuthenticationError):
    """账户被锁定异常"""
    pass


class TokenExpiredError(AuthenticationError):
    """令牌已过期异常"""
    pass


class InvalidTokenError(AuthenticationError):
    """令牌无效异常"""
    pass


class AuthToken:
    """认证令牌容器"""
    
    def __init__(self, access_token: str, refresh_token: str, token_type: str = "Bearer", expires_in: int = 1800):
        """
        初始化认证令牌
        
        参数:
            access_token: 访问令牌
            refresh_token: 刷新令牌
            token_type: 令牌类型（默认 Bearer）
            expires_in: 访问令牌有效期（秒）
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in
        }


class TokenPayload:
    """令牌载荷"""
    
    def __init__(self, user_id: str, username: str, role: str, exp: datetime, token_type: str = "access"):
        """
        初始化令牌载荷
        
        参数:
            user_id: 用户 ID
            username: 用户名
            role: 用户角色
            exp: 过期时间
            token_type: 令牌类型（access 或 refresh）
        """
        self.user_id = user_id
        self.username = username
        self.role = role
        self.exp = exp
        self.token_type = token_type
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "exp": self.exp.timestamp(),
            "token_type": self.token_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenPayload':
        """从字典创建对象"""
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            role=data["role"],
            exp=datetime.fromtimestamp(data["exp"]),
            token_type=data.get("token_type", "access")
        )


class AuthenticationService:
    """
    身份验证服务
    
    提供用户注册、登录、令牌管理和账户锁定功能。
    """
    
    # 密码强度要求
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # 令牌有效期
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # 账户锁定配置
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Redis 键前缀
    REDIS_BLACKLIST_PREFIX = "token:blacklist:"
    REDIS_LOCKOUT_PREFIX = "account:lockout:"
    
    def __init__(self):
        """初始化身份验证服务"""
        self.encryption_service = get_encryption_service()
        self.redis_client = get_redis_client()
        
        # JWT 密钥（从环境变量加载）
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        if not self.jwt_secret:
            # 开发环境：使用固定密钥
            if os.getenv("ENVIRONMENT") == "production":
                raise AuthenticationError("JWT_SECRET_KEY must be set in production")
            self.jwt_secret = "dev_jwt_secret_key_for_testing_only"
        
        self.jwt_algorithm = "HS256"
    
    def _validate_password_strength(self, password: str) -> None:
        """
        验证密码强度
        
        密码要求：
        - 长度 8-128 字符
        - 至少包含一个大写字母
        - 至少包含一个小写字母
        - 至少包含一个数字
        - 至少包含一个特殊字符
        
        参数:
            password: 密码
        
        异常:
            WeakPasswordError: 密码强度不足
        """
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(f"密码长度至少为 {self.MIN_PASSWORD_LENGTH} 个字符")
        
        if len(password) > self.MAX_PASSWORD_LENGTH:
            raise WeakPasswordError(f"密码长度不能超过 {self.MAX_PASSWORD_LENGTH} 个字符")
        
        if not re.search(r'[A-Z]', password):
            raise WeakPasswordError("密码必须包含至少一个大写字母")
        
        if not re.search(r'[a-z]', password):
            raise WeakPasswordError("密码必须包含至少一个小写字母")
        
        if not re.search(r'\d', password):
            raise WeakPasswordError("密码必须包含至少一个数字")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise WeakPasswordError("密码必须包含至少一个特殊字符")
    
    def _is_account_locked(self, user_id: str) -> bool:
        """
        检查账户是否被锁定
        
        参数:
            user_id: 用户 ID
        
        返回:
            bool: 账户是否被锁定
        """
        lockout_key = f"{self.REDIS_LOCKOUT_PREFIX}{user_id}"
        return self.redis_client.exists(lockout_key) > 0
    
    def _lock_account(self, user_id: str, db: Session) -> None:
        """
        锁定账户
        
        参数:
            user_id: 用户 ID
            db: 数据库会话
        """
        # 在 Redis 中设置锁定标记（15 分钟过期）
        lockout_key = f"{self.REDIS_LOCKOUT_PREFIX}{user_id}"
        self.redis_client.setex(
            lockout_key,
            timedelta(minutes=self.LOCKOUT_DURATION_MINUTES),
            "locked"
        )
        
        # 更新数据库中的锁定状态
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_locked = True
            db.commit()
    
    def _unlock_account(self, user_id: str, db: Session) -> None:
        """
        解锁账户
        
        参数:
            user_id: 用户 ID
            db: 数据库会话
        """
        # 删除 Redis 中的锁定标记
        lockout_key = f"{self.REDIS_LOCKOUT_PREFIX}{user_id}"
        self.redis_client.delete(lockout_key)
        
        # 更新数据库中的锁定状态
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_locked = False
            user.failed_login_attempts = 0
            db.commit()
    
    def _increment_failed_attempts(self, user: User, db: Session) -> None:
        """
        增加失败登录次数
        
        参数:
            user: 用户对象
            db: 数据库会话
        """
        user.failed_login_attempts += 1
        db.commit()
        
        # 如果达到最大失败次数，锁定账户
        if user.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            self._lock_account(user.id, db)
    
    def _reset_failed_attempts(self, user: User, db: Session) -> None:
        """
        重置失败登录次数
        
        参数:
            user: 用户对象
            db: 数据库会话
        """
        user.failed_login_attempts = 0
        db.commit()
    
    def _generate_jwt_token(self, payload: TokenPayload) -> str:
        """
        生成 JWT 令牌
        
        参数:
            payload: 令牌载荷
        
        返回:
            str: JWT 令牌
        """
        token_data = payload.to_dict()
        return jwt.encode(token_data, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _decode_jwt_token(self, token: str, verify_exp: bool = True) -> TokenPayload:
        """
        解码 JWT 令牌
        
        参数:
            token: JWT 令牌
            verify_exp: 是否验证过期时间
        
        返回:
            TokenPayload: 令牌载荷
        
        异常:
            TokenExpiredError: 令牌已过期
            InvalidTokenError: 令牌无效
        """
        try:
            options = {"verify_exp": verify_exp} if not verify_exp else {}
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm], options=options)
            return TokenPayload.from_dict(payload)
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("令牌已过期")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"令牌无效: {str(e)}")
    
    def register_user(self, username: str, password: str, email: str, role: str, db: Session) -> User:
        """
        注册新用户
        
        参数:
            username: 用户名（唯一）
            password: 密码（将被哈希存储）
            email: 电子邮件
            role: 用户角色（user, admin, viewer）
            db: 数据库会话
        
        返回:
            User: 创建的用户对象
        
        异常:
            UserAlreadyExistsError: 用户名或邮箱已存在
            WeakPasswordError: 密码强度不足
        """
        # 验证密码强度
        self._validate_password_strength(password)
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise UserAlreadyExistsError(f"用户名 '{username}' 已存在")
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise UserAlreadyExistsError(f"邮箱 '{email}' 已被使用")
        
        # 验证角色
        valid_roles = ["viewer", "user", "admin"]
        if role not in valid_roles:
            role = "user"  # 默认角色
        
        # 哈希密码
        password_hash = self.encryption_service.hash_password(password)
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            is_locked=False,
            failed_login_attempts=0
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def authenticate(self, username: str, password: str, db: Session) -> AuthToken:
        """
        验证用户身份并生成访问令牌
        
        参数:
            username: 用户名
            password: 密码
            db: 数据库会话
        
        返回:
            AuthToken: 包含 JWT 访问令牌和刷新令牌
        
        异常:
            InvalidCredentialsError: 凭证无效
            AccountLockedError: 账户被锁定
        """
        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise InvalidCredentialsError("用户名或密码错误")
        
        # 检查账户是否被锁定
        if user.is_locked or self._is_account_locked(user.id):
            raise AccountLockedError(f"账户已被锁定，请在 {self.LOCKOUT_DURATION_MINUTES} 分钟后重试")
        
        # 检查账户是否激活
        if not user.is_active:
            raise InvalidCredentialsError("账户未激活")
        
        # 验证密码
        if not self.encryption_service.verify_password(password, user.password_hash):
            # 增加失败次数
            self._increment_failed_attempts(user, db)
            raise InvalidCredentialsError("用户名或密码错误")
        
        # 重置失败次数
        self._reset_failed_attempts(user, db)
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()
        
        # 生成访问令牌
        access_token_payload = TokenPayload(
            user_id=user.id,
            username=user.username,
            role=user.role,
            exp=datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            token_type="access"
        )
        access_token = self._generate_jwt_token(access_token_payload)
        
        # 生成刷新令牌
        refresh_token_payload = TokenPayload(
            user_id=user.id,
            username=user.username,
            role=user.role,
            exp=datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            token_type="refresh"
        )
        refresh_token = self._generate_jwt_token(refresh_token_payload)
        
        return AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def verify_token(self, token: str) -> TokenPayload:
        """
        验证访问令牌的有效性
        
        参数:
            token: JWT 访问令牌
        
        返回:
            TokenPayload: 令牌载荷（包含用户 ID、角色、过期时间）
        
        异常:
            TokenExpiredError: 令牌已过期
            InvalidTokenError: 令牌无效或已被撤销
        """
        # 检查令牌是否在黑名单中
        blacklist_key = f"{self.REDIS_BLACKLIST_PREFIX}{token}"
        if self.redis_client.exists(blacklist_key):
            raise InvalidTokenError("令牌已被撤销")
        
        # 解码令牌
        payload = self._decode_jwt_token(token)
        
        # 验证令牌类型
        if payload.token_type != "access":
            raise InvalidTokenError("令牌类型错误")
        
        # 验证过期时间
        if datetime.utcnow() > payload.exp:
            raise TokenExpiredError("令牌已过期")
        
        return payload
    
    def refresh_token(self, refresh_token: str, db: Session) -> AuthToken:
        """
        使用刷新令牌获取新的访问令牌
        
        参数:
            refresh_token: 刷新令牌
            db: 数据库会话
        
        返回:
            AuthToken: 新的访问令牌和刷新令牌
        
        异常:
            InvalidTokenError: 刷新令牌无效
            TokenExpiredError: 刷新令牌已过期
        """
        # 检查令牌是否在黑名单中
        blacklist_key = f"{self.REDIS_BLACKLIST_PREFIX}{refresh_token}"
        if self.redis_client.exists(blacklist_key):
            raise InvalidTokenError("刷新令牌已被撤销")
        
        # 解码令牌
        payload = self._decode_jwt_token(refresh_token)
        
        # 验证令牌类型
        if payload.token_type != "refresh":
            raise InvalidTokenError("令牌类型错误")
        
        # 验证过期时间
        if datetime.utcnow() > payload.exp:
            raise TokenExpiredError("刷新令牌已过期")
        
        # 验证用户是否仍然存在且激活
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user or not user.is_active:
            raise InvalidTokenError("用户不存在或未激活")
        
        # 生成新的访问令牌
        access_token_payload = TokenPayload(
            user_id=user.id,
            username=user.username,
            role=user.role,
            exp=datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            token_type="access"
        )
        access_token = self._generate_jwt_token(access_token_payload)
        
        # 生成新的刷新令牌
        new_refresh_token_payload = TokenPayload(
            user_id=user.id,
            username=user.username,
            role=user.role,
            exp=datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            token_type="refresh"
        )
        new_refresh_token = self._generate_jwt_token(new_refresh_token_payload)
        
        # 将旧的刷新令牌加入黑名单
        self.revoke_token(refresh_token)
        
        return AuthToken(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def revoke_token(self, token: str) -> bool:
        """
        撤销访问令牌（加入黑名单）
        
        参数:
            token: 要撤销的令牌
        
        返回:
            bool: 撤销是否成功
        """
        try:
            # 解码令牌以获取过期时间（不验证过期）
            payload = self._decode_jwt_token(token, verify_exp=False)
            
            # 计算令牌剩余有效时间
            remaining_time = payload.exp - datetime.utcnow()
            if remaining_time.total_seconds() <= 0:
                # 令牌已过期，无需加入黑名单
                return True
            
            # 将令牌加入黑名单（设置过期时间为令牌的剩余有效时间）
            blacklist_key = f"{self.REDIS_BLACKLIST_PREFIX}{token}"
            self.redis_client.setex(
                blacklist_key,
                remaining_time,
                "revoked"
            )
            
            return True
        except (TokenExpiredError, InvalidTokenError):
            # 令牌无效或已过期，视为撤销成功
            return True
        except Exception:
            return False


# 全局单例实例
_authentication_service: Optional[AuthenticationService] = None


def get_authentication_service() -> AuthenticationService:
    """
    获取身份验证服务单例实例
    
    返回:
        AuthenticationService: 身份验证服务实例
    """
    global _authentication_service
    if _authentication_service is None:
        _authentication_service = AuthenticationService()
    return _authentication_service
