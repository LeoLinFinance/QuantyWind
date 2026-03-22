"""
审计日志路由独立测试

不依赖完整应用的独立测试
"""

import pytest
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.config import Base, get_db
from backend.models.user import User
from backend.models.audit_log import AuditLog
from backend.services.authentication_service import AuthenticationService
from backend.services.encryption_service import EncryptionService
from backend.routers.audit import router as audit_router


# 测试数据库设置
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_audit_router_standalone.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 创建测试应用
app = FastAPI()
app.include_router(audit_router)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def encryption_service():
    """创建加密服务实例"""
    return EncryptionService()


@pytest.fixture
def admin_user(db_session, encryption_service):
    """创建管理员用户"""
    user = User(
        username="admin",
        email="admin@test.com",
        password_hash=encryption_service.hash_password("Admin123!"),
        role="admin",
        is_active=True,
        is_locked=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session, encryption_service):
    """创建普通用户"""
    user = User(
        username="user",
        email="user@test.com",
        password_hash=encryption_service.hash_password("User123!"),
        role="user",
        is_active=True,
        is_locked=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(db_session, admin_user):
    """生成管理员访问令牌"""
    auth_service = AuthenticationService()
    auth_token = auth_service.authenticate(admin_user.username, "Admin123!", db_session)
    return auth_token.access_token


@pytest.fixture
def user_token(db_session, regular_user):
    """生成普通用户访问令牌"""
    auth_service = AuthenticationService()
    auth_token = auth_service.authenticate(regular_user.username, "User123!", db_session)
    return auth_token.access_token


@pytest.fixture
def sample_audit_logs(db_session, admin_user, regular_user):
    """创建示例审计日志"""
    logs = []
    
    # 认证日志
    logs.append(AuditLog(
        event_type="authentication",
        action="login",
        user_id=admin_user.id,
        ip_address="192.168.1.100",
        success=True,
        severity="info",
        details={"user_agent": "TestAgent/1.0"}
    ))
    
    logs.append(AuditLog(
        event_type="authentication",
        action="login",
        user_id=regular_user.id,
        ip_address="192.168.1.101",
        success=False,
        severity="medium",
        details={"reason": "invalid_password"}
    ))
    
    # 授权日志
    logs.append(AuditLog(
        event_type="authorization",
        action="read_user_management",
        user_id=admin_user.id,
        resource="user_management",
        success=True,
        severity="info",
        details={}
    ))
    
    # 安全事件
    logs.append(AuditLog(
        event_type="security_event",
        action="account_locked",
        user_id=regular_user.id,
        ip_address="192.168.1.101",
        success=False,
        severity="high",
        details={
            "description": "Account locked due to 5 failed login attempts",
            "failed_attempts": 5
        }
    ))
    
    logs.append(AuditLog(
        event_type="security_event",
        action="suspicious_activity",
        user_id=regular_user.id,
        ip_address="192.168.1.102",
        success=False,
        severity="critical",
        details={
            "description": "IP address changed during session",
            "old_ip": "192.168.1.101",
            "new_ip": "192.168.1.102"
        }
    ))
    
    for log in logs:
        db_session.add(log)
    
    db_session.commit()
    return logs


def test_get_logs_as_admin_success(db_session, admin_token, sample_audit_logs):
    """测试管理员成功获取审计日志"""
    response = client.get(
        "/api/audit/logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data
    assert data["total"] >= 5  # 至少有示例日志


def test_get_logs_as_regular_user_denied(db_session, user_token, sample_audit_logs):
    """测试普通用户无法获取审计日志"""
    response = client.get(
        "/api/audit/logs",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    assert "管理员权限" in response.json()["detail"]


def test_get_logs_with_event_type_filter(db_session, admin_token, sample_audit_logs):
    """测试按事件类型过滤"""
    response = client.get(
        "/api/audit/logs?event_type=authentication",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(log["event_type"] == "authentication" for log in data["logs"])


def test_get_logs_with_pagination(db_session, admin_token, sample_audit_logs):
    """测试分页功能"""
    response = client.get(
        "/api/audit/logs?page=1&page_size=2",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["logs"]) <= 2


def test_get_security_events_as_admin_success(db_session, admin_token, sample_audit_logs):
    """测试管理员成功获取安全事件"""
    response = client.get(
        "/api/audit/security-events",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "total" in data
    # 应该有 2 个安全事件
    assert data["total"] == 2
    assert all(event["event_type"] == "security_event" for event in data["events"])


def test_get_security_events_as_regular_user_denied(db_session, user_token, sample_audit_logs):
    """测试普通用户无法获取安全事件"""
    response = client.get(
        "/api/audit/security-events",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    assert "管理员权限" in response.json()["detail"]


def test_get_security_events_with_severity_filter(db_session, admin_token, sample_audit_logs):
    """测试按严重程度过滤安全事件"""
    response = client.get(
        "/api/audit/security-events?severity=high",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(event["severity"] == "high" for event in data["events"])


def test_get_logs_with_invalid_date_format(db_session, admin_token):
    """测试无效的日期格式"""
    response = client.get(
        "/api/audit/logs?start_date=invalid-date",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400
    assert "无效的日期格式" in response.json()["detail"]


def test_get_security_events_with_invalid_severity(db_session, admin_token):
    """测试无效的严重程度"""
    response = client.get(
        "/api/audit/security-events?severity=invalid",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400
    assert "无效的严重程度" in response.json()["detail"]


def test_get_logs_returns_correct_structure(db_session, admin_token, sample_audit_logs):
    """测试返回的日志结构正确"""
    response = client.get(
        "/api/audit/logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # 检查响应结构
    assert "logs" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "filters" in data
    
    # 检查日志条目结构
    if data["logs"]:
        log = data["logs"][0]
        assert "id" in log
        assert "timestamp" in log
        assert "event_type" in log
        assert "action" in log
        assert "success" in log
        assert "severity" in log
        assert "details" in log


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
