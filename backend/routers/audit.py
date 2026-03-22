"""
审计日志路由模块

提供审计日志查询相关的 API 端点：
- GET /api/audit/logs - 查询审计日志（仅管理员）
- GET /api/audit/security-events - 查询安全事件（仅管理员）

需求：7.4
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.config import get_db
from backend.services.audit_log_service import AuditLogService
from backend.services.authorization_service import AuthorizationService
from backend.middleware.auth_middleware import (
    get_current_user,
    TokenPayload,
    PermissionDeniedError
)


router = APIRouter(prefix="/api/audit", tags=["audit"])


# Pydantic 模型
class AuditLogResponse(BaseModel):
    """审计日志响应模型"""
    id: str
    timestamp: str
    event_type: str
    action: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    resource: Optional[str] = None
    success: bool
    severity: str
    details: dict
    
    class Config:
        from_attributes = True


class AuditLogsResponse(BaseModel):
    """审计日志列表响应模型"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    filters: dict


class SecurityEventsResponse(BaseModel):
    """安全事件列表响应模型"""
    events: List[AuditLogResponse]
    total: int
    severity_filter: Optional[str] = None


# 辅助函数
def require_admin(
    current_user: TokenPayload,
    db: Session
) -> None:
    """
    检查当前用户是否为管理员
    
    Args:
        current_user: 当前用户令牌载荷
        db: 数据库会话
    
    Raises:
        PermissionDeniedError: 如果用户不是管理员
    """
    auth_service = AuthorizationService(db)
    if not auth_service.is_admin(current_user.user_id):
        raise PermissionDeniedError(detail="此操作需要管理员权限")


def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    解析日期时间字符串
    
    支持格式：
    - ISO 8601: 2024-01-15T10:30:45
    - 日期: 2024-01-15
    
    Args:
        date_str: 日期时间字符串
    
    Returns:
        datetime: 解析后的日期时间对象，如果输入为 None 则返回 None
    
    Raises:
        HTTPException: 如果日期格式无效
    """
    if not date_str:
        return None
    
    try:
        # 尝试解析 ISO 8601 格式
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # 尝试解析日期格式（假设为当天开始）
            return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的日期格式: {date_str}。请使用 ISO 8601 格式（如 2024-01-15T10:30:45）或日期格式（如 2024-01-15）"
        )


# API 端点
@router.get("/logs", response_model=AuditLogsResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    event_type: Optional[str] = Query(None, description="事件类型（authentication, authorization, security_event）"),
    user_id: Optional[str] = Query(None, description="用户 ID"),
    action: Optional[str] = Query(None, description="操作类型"),
    success: Optional[bool] = Query(None, description="是否成功"),
    severity: Optional[str] = Query(None, description="严重程度（low, medium, high, critical）"),
    ip_address: Optional[str] = Query(None, description="IP 地址"),
    resource: Optional[str] = Query(None, description="资源"),
    start_date: Optional[str] = Query(None, description="开始日期（ISO 8601 格式或 YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（ISO 8601 格式或 YYYY-MM-DD）"),
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询审计日志（仅管理员）
    
    支持多种过滤条件和分页功能
    
    Args:
        page: 页码（从 1 开始）
        page_size: 每页数量（1-200）
        event_type: 按事件类型过滤（可选）
        user_id: 按用户 ID 过滤（可选）
        action: 按操作类型过滤（可选）
        success: 按成功状态过滤（可选）
        severity: 按严重程度过滤（可选）
        ip_address: 按 IP 地址过滤（可选）
        resource: 按资源过滤（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        AuditLogsResponse: 审计日志列表响应
    
    Raises:
        PermissionDeniedError: 如果用户不是管理员
        HTTPException: 如果日期格式无效
    """
    # 检查管理员权限
    require_admin(current_user, db)
    
    # 记录审计日志访问
    audit_service = AuditLogService(db)
    audit_service.log_authorization(
        user_id=current_user.user_id,
        resource="audit_logs",
        action="read",
        granted=True,
        reason="admin_access"
    )
    
    # 解析日期时间
    start_time = parse_datetime(start_date)
    end_time = parse_datetime(end_date)
    
    # 如果只提供了日期（没有时间），将结束日期设置为当天结束
    if end_time and not end_date.count('T'):
        end_time = end_time.replace(hour=23, minute=59, second=59)
    
    # 构建过滤条件
    filters = {}
    if event_type:
        filters["event_type"] = event_type
    if user_id:
        filters["user_id"] = user_id
    if action:
        filters["action"] = action
    if success is not None:
        filters["success"] = success
    if severity:
        filters["severity"] = severity
    if ip_address:
        filters["ip_address"] = ip_address
    if resource:
        filters["resource"] = resource
    
    # 查询日志（不分页，用于获取总数）
    all_logs = audit_service.query_logs(
        filters=filters,
        start_time=start_time,
        end_time=end_time,
        limit=10000,  # 设置一个较大的限制以获取所有匹配的日志
        offset=0
    )
    total = len(all_logs)
    
    # 应用分页
    offset = (page - 1) * page_size
    logs = audit_service.query_logs(
        filters=filters,
        start_time=start_time,
        end_time=end_time,
        limit=page_size,
        offset=offset
    )
    
    # 转换为响应模型
    log_responses = []
    for log in logs:
        log_responses.append(AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp.isoformat() if log.timestamp else None,
            event_type=log.event_type,
            action=log.action,
            user_id=log.user_id,
            ip_address=log.ip_address,
            resource=log.resource,
            success=log.success,
            severity=log.severity,
            details=log.details or {}
        ))
    
    return AuditLogsResponse(
        logs=log_responses,
        total=total,
        page=page,
        page_size=page_size,
        filters=filters
    )


@router.get("/security-events", response_model=SecurityEventsResponse)
async def get_security_events(
    severity: Optional[str] = Query(None, description="严重程度过滤（low, medium, high, critical）"),
    hours: int = Query(24, ge=1, le=720, description="查询最近多少小时的事件（默认 24 小时，最多 30 天）"),
    limit: int = Query(100, ge=1, le=500, description="返回结果数量限制"),
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询安全事件（仅管理员）
    
    返回最近的安全事件，按时间倒序排列
    
    Args:
        severity: 按严重程度过滤（可选）
        hours: 查询最近多少小时的事件（默认 24 小时）
        limit: 返回结果数量限制（1-500）
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        SecurityEventsResponse: 安全事件列表响应
    
    Raises:
        PermissionDeniedError: 如果用户不是管理员
        HTTPException: 如果严重程度无效
    """
    # 检查管理员权限
    require_admin(current_user, db)
    
    # 验证严重程度
    if severity:
        valid_severities = ["low", "medium", "high", "critical"]
        if severity not in valid_severities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的严重程度。有效值：{', '.join(valid_severities)}"
            )
    
    # 记录审计日志访问
    audit_service = AuditLogService(db)
    audit_service.log_authorization(
        user_id=current_user.user_id,
        resource="security_events",
        action="read",
        granted=True,
        reason="admin_access"
    )
    
    # 计算开始时间
    from datetime import timezone
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start_time = now - timedelta(hours=hours)
    
    # 查询安全事件
    events = audit_service.get_security_events(
        severity=severity,
        start_time=start_time,
        limit=limit
    )
    
    # 转换为响应模型
    event_responses = []
    for event in events:
        event_responses.append(AuditLogResponse(
            id=event.id,
            timestamp=event.timestamp.isoformat() if event.timestamp else None,
            event_type=event.event_type,
            action=event.action,
            user_id=event.user_id,
            ip_address=event.ip_address,
            resource=event.resource,
            success=event.success,
            severity=event.severity,
            details=event.details or {}
        ))
    
    return SecurityEventsResponse(
        events=event_responses,
        total=len(event_responses),
        severity_filter=severity
    )
