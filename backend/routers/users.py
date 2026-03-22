"""
用户管理路由模块

提供用户管理相关的 API 端点：
- GET /api/users - 获取用户列表（仅管理员）
- GET /api/users/{id} - 获取用户详情
- PUT /api/users/{id}/role - 更新用户角色（仅管理员）
- DELETE /api/users/{id} - 删除用户（仅管理员）

需求：6.2, 6.5
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.config import get_db
from backend.models.user import User
from backend.services.authorization_service import AuthorizationService
from backend.services.audit_log_service import AuditLogService
from backend.middleware.auth_middleware import (
    get_current_user,
    TokenPayload,
    PermissionDeniedError
)


router = APIRouter(prefix="/api/users", tags=["users"])


# Pydantic 模型
class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    is_locked: bool
    last_login: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class UpdateRoleRequest(BaseModel):
    """更新角色请求模型"""
    role: str = Field(..., description="新角色（viewer, user, admin）")


class UpdateRoleResponse(BaseModel):
    """更新角色响应模型"""
    success: bool
    message: str
    user: UserResponse


class DeleteUserResponse(BaseModel):
    """删除用户响应模型"""
    success: bool
    message: str


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


# API 端点
@router.get("", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[str] = Query(None, description="按角色过滤"),
    is_active: Optional[bool] = Query(None, description="按激活状态过滤"),
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（仅管理员）
    
    支持分页和过滤功能
    
    Args:
        page: 页码（从 1 开始）
        page_size: 每页数量（1-100）
        role: 按角色过滤（可选）
        is_active: 按激活状态过滤（可选）
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        UserListResponse: 用户列表响应
    
    Raises:
        PermissionDeniedError: 如果用户不是管理员
    """
    # 检查管理员权限
    require_admin(current_user, db)
    
    # 记录审计日志
    audit_service = AuditLogService(db)
    audit_service.log_authorization(
        user_id=current_user.user_id,
        resource="user_management",
        action="read",
        granted=True,
        reason="admin_access"
    )
    
    # 构建查询
    query = db.query(User)
    
    # 应用过滤条件
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()
    
    # 转换为响应模型
    user_responses = [UserResponse.from_orm(user) for user in users]
    
    return UserListResponse(
        users=user_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户详情
    
    用户可以查看自己的信息，管理员可以查看任何用户的信息
    
    Args:
        user_id: 用户 ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        UserResponse: 用户详情
    
    Raises:
        HTTPException: 如果用户不存在或无权限访问
    """
    # 检查权限：用户只能查看自己的信息，管理员可以查看所有用户
    auth_service = AuthorizationService(db)
    is_admin = auth_service.is_admin(current_user.user_id)
    
    if not is_admin and current_user.user_id != user_id:
        # 记录未授权访问尝试
        audit_service = AuditLogService(db)
        audit_service.log_authorization(
            user_id=current_user.user_id,
            resource="user_management",
            action="read",
            granted=False,
            reason="not_admin_or_self"
        )
        raise PermissionDeniedError(detail="您只能查看自己的用户信息")
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )
    
    # 记录审计日志
    audit_service = AuditLogService(db)
    audit_service.log_authorization(
        user_id=current_user.user_id,
        resource="user_management",
        action="read",
        granted=True,
        reason="admin_access" if is_admin else "self_access"
    )
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}/role", response_model=UpdateRoleResponse)
async def update_user_role(
    user_id: str,
    request: UpdateRoleRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户角色（仅管理员）
    
    Args:
        user_id: 用户 ID
        request: 更新角色请求
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        UpdateRoleResponse: 更新结果
    
    Raises:
        PermissionDeniedError: 如果用户不是管理员
        HTTPException: 如果用户不存在或角色无效
    """
    # 检查管理员权限
    require_admin(current_user, db)
    
    # 验证角色
    valid_roles = ["viewer", "user", "admin"]
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的角色。有效角色：{', '.join(valid_roles)}"
        )
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )
    
    # 防止管理员修改自己的角色
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )
    
    # 记录旧角色
    old_role = user.role
    
    # 更新角色
    auth_service = AuthorizationService(db)
    try:
        success = auth_service.update_role(user_id, request.role)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新角色失败"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # 刷新用户对象
    db.refresh(user)
    
    # 记录审计日志
    audit_service = AuditLogService(db)
    audit_service.log_authorization(
        user_id=current_user.user_id,
        resource="user_management",
        action="write",
        granted=True,
        reason=f"role_updated_from_{old_role}_to_{request.role}"
    )
    
    # 记录安全事件（角色变更是重要的安全事件）
    audit_service.log_security_event(
        event_type="role_changed",
        severity="medium",
        description=f"用户 {user.username} 的角色从 {old_role} 更改为 {request.role}",
        metadata={
            "target_user_id": user_id,
            "target_username": user.username,
            "old_role": old_role,
            "new_role": request.role,
            "changed_by": current_user.username
        },
        user_id=current_user.user_id
    )
    
    return UpdateRoleResponse(
        success=True,
        message=f"用户角色已从 {old_role} 更新为 {request.role}",
        user=UserResponse.from_orm(user)
    )


@router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(
    user_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户（仅管理员）
    
    注意：这是软删除，将用户标记为非激活状态
    
    Args:
        user_id: 用户 ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        DeleteUserResponse: 删除结果
    
    Raises:
        PermissionDeniedError: 如果用户不是管理员
        HTTPException: 如果用户不存在或尝试删除自己
    """
    # 检查管理员权限
    require_admin(current_user, db)
    
    # 防止管理员删除自己
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )
    
    # 软删除：标记为非激活
    user.is_active = False
    db.commit()
    
    # 记录审计日志
    audit_service = AuditLogService(db)
    audit_service.log_authorization(
        user_id=current_user.user_id,
        resource="user_management",
        action="delete",
        granted=True,
        reason="user_deactivated"
    )
    
    # 记录安全事件
    audit_service.log_security_event(
        event_type="user_deleted",
        severity="high",
        description=f"用户 {user.username} 已被停用",
        metadata={
            "target_user_id": user_id,
            "target_username": user.username,
            "target_email": user.email,
            "target_role": user.role,
            "deleted_by": current_user.username
        },
        user_id=current_user.user_id
    )
    
    return DeleteUserResponse(
        success=True,
        message=f"用户 {user.username} 已被停用"
    )
