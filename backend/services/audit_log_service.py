"""
审计日志服务
用于记录所有安全相关事件，包括身份验证、授权和系统操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from models.audit_log import AuditLog
from database.config import get_db


class AuditLogService:
    """
    审计日志服务类
    
    提供日志记录、查询和管理功能
    """
    
    def __init__(self, db: Session):
        """
        初始化审计日志服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def log_authentication(
        self,
        user_id: Optional[str],
        action: str,
        success: bool,
        ip_address: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        记录身份验证事件
        
        Args:
            user_id: 用户 ID（可选，注册时可能还没有 ID）
            action: 操作类型（login, logout, register, token_refresh）
            success: 是否成功
            ip_address: IP 地址
            details: 额外详情（如 user_agent, session_id, failure_reason）
        
        Returns:
            AuditLog: 创建的审计日志对象
        
        Examples:
            >>> service.log_authentication(
            ...     user_id="user_123",
            ...     action="login",
            ...     success=True,
            ...     ip_address="192.168.1.100",
            ...     details={"user_agent": "Mozilla/5.0", "session_id": "sess_xyz"}
            ... )
        """
        # 确定严重程度
        if not success:
            severity = "medium"  # 失败的认证尝试需要关注
        else:
            severity = "info"
        
        log_entry = AuditLog(
            event_type="authentication",
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            severity=severity,
            details=details or {}
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        reason: Optional[str] = None
    ) -> AuditLog:
        """
        记录授权检查事件
        
        Args:
            user_id: 用户 ID
            resource: 资源标识符（如 "portfolio", "market_data"）
            action: 操作类型（如 "read", "write", "delete"）
            granted: 是否授权
            reason: 原因（如 "insufficient_permissions", "role_mismatch"）
        
        Returns:
            AuditLog: 创建的审计日志对象
        
        Examples:
            >>> service.log_authorization(
            ...     user_id="user_123",
            ...     resource="user_management",
            ...     action="write",
            ...     granted=False,
            ...     reason="insufficient_permissions"
            ... )
        """
        # 未授权的访问尝试需要更高的关注度
        severity = "info" if granted else "medium"
        
        details = {
            "reason": reason
        } if reason else {}
        
        log_entry = AuditLog(
            event_type="authorization",
            action=f"{action}_{resource}",
            user_id=user_id,
            resource=resource,
            success=granted,
            severity=severity,
            details=details
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        记录安全事件
        
        Args:
            event_type: 事件类型（intrusion_attempt, suspicious_activity, 
                       account_locked, session_hijack, etc.）
            severity: 严重程度（low, medium, high, critical）
            description: 事件描述
            metadata: 元数据（额外的上下文信息）
            user_id: 相关用户 ID（可选）
            ip_address: 相关 IP 地址（可选）
        
        Returns:
            AuditLog: 创建的审计日志对象
        
        Examples:
            >>> service.log_security_event(
            ...     event_type="account_locked",
            ...     severity="high",
            ...     description="Account locked due to 5 failed login attempts",
            ...     metadata={"failed_attempts": 5, "lock_duration": "15 minutes"},
            ...     user_id="user_123",
            ...     ip_address="192.168.1.100"
            ... )
        """
        # 验证严重程度
        valid_severities = ["low", "medium", "high", "critical"]
        if severity not in valid_severities:
            severity = "medium"  # 默认值
        
        details = metadata or {}
        details["description"] = description
        
        log_entry = AuditLog(
            event_type="security_event",
            action=event_type,
            user_id=user_id,
            ip_address=ip_address,
            success=False,  # 安全事件通常表示异常情况
            severity=severity,
            details=details
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    def query_logs(
        self,
        filters: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        查询审计日志
        
        Args:
            filters: 过滤条件字典，支持的键：
                - event_type: 事件类型
                - user_id: 用户 ID
                - action: 操作类型
                - success: 是否成功
                - severity: 严重程度
                - ip_address: IP 地址
            start_time: 开始时间（包含）
            end_time: 结束时间（包含）
            limit: 返回结果数量限制（默认 100）
            offset: 偏移量（用于分页）
        
        Returns:
            List[AuditLog]: 审计日志列表，按时间倒序排列
        
        Examples:
            >>> # 查询最近 24 小时的失败登录尝试
            >>> service.query_logs(
            ...     filters={"event_type": "authentication", "success": False},
            ...     start_time=datetime.now() - timedelta(days=1)
            ... )
        """
        query = self.db.query(AuditLog)
        
        # 应用时间范围过滤
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)
        
        # 应用其他过滤条件
        if filters:
            if "event_type" in filters:
                query = query.filter(AuditLog.event_type == filters["event_type"])
            if "user_id" in filters:
                query = query.filter(AuditLog.user_id == filters["user_id"])
            if "action" in filters:
                query = query.filter(AuditLog.action == filters["action"])
            if "success" in filters:
                query = query.filter(AuditLog.success == filters["success"])
            if "severity" in filters:
                query = query.filter(AuditLog.severity == filters["severity"])
            if "ip_address" in filters:
                query = query.filter(AuditLog.ip_address == filters["ip_address"])
        
        # 按时间倒序排列
        query = query.order_by(desc(AuditLog.timestamp))
        
        # 应用分页
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_failed_login_attempts(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        time_window: timedelta = timedelta(minutes=15)
    ) -> int:
        """
        获取指定时间窗口内的失败登录次数
        
        Args:
            user_id: 用户 ID（可选）
            ip_address: IP 地址（可选）
            time_window: 时间窗口（默认 15 分钟）
        
        Returns:
            int: 失败登录次数
        
        Examples:
            >>> # 获取用户最近 15 分钟的失败登录次数
            >>> count = service.get_failed_login_attempts(user_id="user_123")
        """
        # 使用 UTC 时间以与数据库保持一致（SQLite 的 func.now() 返回 UTC）
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)  # 转换为 naive datetime
        start_time = now - time_window
        
        query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.event_type == "authentication",
                AuditLog.action == "login",
                AuditLog.success == False,
                AuditLog.timestamp >= start_time
            )
        )
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if ip_address:
            query = query.filter(AuditLog.ip_address == ip_address)
        
        return query.count()
    
    def get_security_events(
        self,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        获取安全事件日志
        
        Args:
            severity: 严重程度过滤（可选）
            start_time: 开始时间（可选）
            limit: 返回结果数量限制
        
        Returns:
            List[AuditLog]: 安全事件日志列表
        
        Examples:
            >>> # 获取最近的高危安全事件
            >>> events = service.get_security_events(
            ...     severity="high",
            ...     start_time=datetime.now() - timedelta(hours=1)
            ... )
        """
        query = self.db.query(AuditLog).filter(
            AuditLog.event_type == "security_event"
        )
        
        if severity:
            query = query.filter(AuditLog.severity == severity)
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        
        query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
        
        return query.all()
    
    def get_user_activity(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        获取用户活动日志
        
        Args:
            user_id: 用户 ID
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 返回结果数量限制
        
        Returns:
            List[AuditLog]: 用户活动日志列表
        
        Examples:
            >>> # 获取用户今天的所有活动
            >>> activity = service.get_user_activity(
            ...     user_id="user_123",
            ...     start_time=datetime.now().replace(hour=0, minute=0, second=0)
            ... )
        """
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)
        
        query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
        
        return query.all()
    
    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """
        清理旧日志
        
        Args:
            retention_days: 保留天数（默认 90 天）
        
        Returns:
            int: 删除的日志数量
        
        Examples:
            >>> # 删除 90 天前的日志
            >>> deleted_count = service.cleanup_old_logs()
        """
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cutoff_date = now - timedelta(days=retention_days)
        
        # 查询要删除的日志数量
        count = self.db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).count()
        
        # 删除旧日志
        self.db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        
        return count
    
    def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取审计日志统计信息
        
        Args:
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
        
        Returns:
            Dict[str, Any]: 统计信息字典，包含：
                - total_events: 总事件数
                - by_event_type: 按事件类型分组的计数
                - by_severity: 按严重程度分组的计数
                - failed_authentications: 失败的认证次数
                - denied_authorizations: 被拒绝的授权次数
        
        Examples:
            >>> # 获取今天的统计信息
            >>> stats = service.get_statistics(
            ...     start_time=datetime.now().replace(hour=0, minute=0, second=0)
            ... )
        """
        query = self.db.query(AuditLog)
        
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)
        
        # 总事件数
        total_events = query.count()
        
        # 按事件类型统计
        by_event_type = {}
        for event_type in ["authentication", "authorization", "security_event"]:
            count = query.filter(AuditLog.event_type == event_type).count()
            by_event_type[event_type] = count
        
        # 按严重程度统计
        by_severity = {}
        for severity in ["low", "medium", "high", "critical"]:
            count = query.filter(AuditLog.severity == severity).count()
            by_severity[severity] = count
        
        # 失败的认证次数
        failed_authentications = query.filter(
            and_(
                AuditLog.event_type == "authentication",
                AuditLog.success == False
            )
        ).count()
        
        # 被拒绝的授权次数
        denied_authorizations = query.filter(
            and_(
                AuditLog.event_type == "authorization",
                AuditLog.success == False
            )
        ).count()
        
        return {
            "total_events": total_events,
            "by_event_type": by_event_type,
            "by_severity": by_severity,
            "failed_authentications": failed_authentications,
            "denied_authorizations": denied_authorizations
        }


def get_audit_log_service(db: Session) -> AuditLogService:
    """
    获取审计日志服务实例
    用于依赖注入
    
    Args:
        db: 数据库会话
    
    Returns:
        AuditLogService: 审计日志服务实例
    """
    return AuditLogService(db)
