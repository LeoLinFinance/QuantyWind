"""
审计日志路由测试

测试审计日志查询 API 端点的功能
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from backend.main import app
from backend.database.config import Base, get_db
from backend.models.user import User
from backend.models.audit_log import AuditLog
from backend.services.authentication_service import AuthenticationService
from backend.services.encryption_service import EncryptionService


# 测试数据库设置
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_audit_router.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    auth_service = AuthenticationService(db_session)
    auth_token = auth_service.authenticate(admin_user.username, "Admin123!")
    return auth_token.access_token


@pytest.fixture
def user_token(db_session, regular_user):
    """生成普通用户访问令牌"""
    auth_service = AuthenticationService(db_session)
    auth_token = auth_service.authenticate(regular_user.username, "User123!")
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
    
    logs.append(AuditLog(
        event_type="authorization",
        action="write_user_management",
        user_id=regular_user.id,
        resource="user_management",
        success=False,
        severity="medium",
        details={"reason": "insufficient_permissions"}
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


class TestGetAuditLogs:
    """测试获取审计日志端点"""
    
    def test_get_logs_as_admin_success(self, db_session, admin_token, sample_audit_logs):
        """测试管理员成功获取审计日志"""
        response = client.get(
            "/api/audit/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert data["total"] == len(sample_audit_logs)
        assert len(data["logs"]) == len(sample_audit_logs)
    
    def test_get_logs_as_regular_user_denied(self, db_session, user_token, sample_audit_logs):
        """测试普通用户无法获取审计日志"""
        response = client.get(
            "/api/audit/logs",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
        assert "管理员权限" in response.json()["detail"]
    
    def test_get_logs_without_auth_denied(self, db_session, sample_audit_logs):
        """测试未认证用户无法获取审计日志"""
        response = client.get("/api/audit/logs")
        
        assert response.status_code == 403
    
    def test_get_logs_with_event_type_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按事件类型过滤"""
        response = client.get(
            "/api/audit/logs?event_type=authentication",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(log["event_type"] == "authentication" for log in data["logs"])
    
    def test_get_logs_with_user_id_filter(self, db_session, admin_token, sample_audit_logs, regular_user):
        """测试按用户 ID 过滤"""
        response = client.get(
            f"/api/audit/logs?user_id={regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(log["user_id"] == regular_user.id for log in data["logs"])
    
    def test_get_logs_with_success_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按成功状态过滤"""
        response = client.get(
            "/api/audit/logs?success=false",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(log["success"] is False for log in data["logs"])
    
    def test_get_logs_with_severity_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按严重程度过滤"""
        response = client.get(
            "/api/audit/logs?severity=high",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(log["severity"] == "high" for log in data["logs"])
    
    def test_get_logs_with_ip_address_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按 IP 地址过滤"""
        response = client.get(
            "/api/audit/logs?ip_address=192.168.1.100",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(log["ip_address"] == "192.168.1.100" for log in data["logs"])
    
    def test_get_logs_with_resource_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按资源过滤"""
        response = client.get(
            "/api/audit/logs?resource=user_management",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(log["resource"] == "user_management" for log in data["logs"])
    
    def test_get_logs_with_action_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按操作类型过滤"""
        response = client.get(
            "/api/audit/logs?action=login",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(log["action"] == "login" for log in data["logs"])
    
    def test_get_logs_with_date_range(self, db_session, admin_token, sample_audit_logs):
        """测试按日期范围过滤"""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/audit/logs?start_date={today}&end_date={tomorrow}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == len(sample_audit_logs)
    
    def test_get_logs_with_invalid_date_format(self, db_session, admin_token):
        """测试无效的日期格式"""
        response = client.get(
            "/api/audit/logs?start_date=invalid-date",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "无效的日期格式" in response.json()["detail"]
    
    def test_get_logs_with_pagination(self, db_session, admin_token, sample_audit_logs):
        """测试分页功能"""
        # 第一页
        response = client.get(
            "/api/audit/logs?page=1&page_size=2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["logs"]) == 2
        assert data["total"] == len(sample_audit_logs)
        
        # 第二页
        response = client.get(
            "/api/audit/logs?page=2&page_size=2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert len(data["logs"]) == 2
    
    def test_get_logs_with_multiple_filters(self, db_session, admin_token, sample_audit_logs):
        """测试多个过滤条件组合"""
        response = client.get(
            "/api/audit/logs?event_type=authentication&success=false",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(
            log["event_type"] == "authentication" and log["success"] is False
            for log in data["logs"]
        )
    
    def test_get_logs_returns_correct_structure(self, db_session, admin_token, sample_audit_logs):
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


class TestGetSecurityEvents:
    """测试获取安全事件端点"""
    
    def test_get_security_events_as_admin_success(self, db_session, admin_token, sample_audit_logs):
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
    
    def test_get_security_events_as_regular_user_denied(self, db_session, user_token, sample_audit_logs):
        """测试普通用户无法获取安全事件"""
        response = client.get(
            "/api/audit/security-events",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
        assert "管理员权限" in response.json()["detail"]
    
    def test_get_security_events_without_auth_denied(self, db_session, sample_audit_logs):
        """测试未认证用户无法获取安全事件"""
        response = client.get("/api/audit/security-events")
        
        assert response.status_code == 403
    
    def test_get_security_events_with_severity_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按严重程度过滤安全事件"""
        response = client.get(
            "/api/audit/security-events?severity=high",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(event["severity"] == "high" for event in data["events"])
        assert data["severity_filter"] == "high"
    
    def test_get_security_events_with_invalid_severity(self, db_session, admin_token):
        """测试无效的严重程度"""
        response = client.get(
            "/api/audit/security-events?severity=invalid",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "无效的严重程度" in response.json()["detail"]
    
    def test_get_security_events_with_hours_filter(self, db_session, admin_token, sample_audit_logs):
        """测试按时间范围过滤"""
        response = client.get(
            "/api/audit/security-events?hours=1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # 所有事件都应该在最近 1 小时内（因为是刚创建的）
        assert data["total"] == 2
    
    def test_get_security_events_with_limit(self, db_session, admin_token, sample_audit_logs):
        """测试结果数量限制"""
        response = client.get(
            "/api/audit/security-events?limit=1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
    
    def test_get_security_events_returns_correct_structure(self, db_session, admin_token, sample_audit_logs):
        """测试返回的安全事件结构正确"""
        response = client.get(
            "/api/audit/security-events",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 检查响应结构
        assert "events" in data
        assert "total" in data
        assert "severity_filter" in data
        
        # 检查事件条目结构
        if data["events"]:
            event = data["events"][0]
            assert "id" in event
            assert "timestamp" in event
            assert "event_type" in event
            assert "action" in event
            assert "success" in event
            assert "severity" in event
            assert "details" in event
            assert event["event_type"] == "security_event"
    
    def test_get_security_events_ordered_by_time(self, db_session, admin_token, sample_audit_logs):
        """测试安全事件按时间倒序排列"""
        response = client.get(
            "/api/audit/security-events",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 检查时间戳是否按倒序排列
        timestamps = [event["timestamp"] for event in data["events"]]
        assert timestamps == sorted(timestamps, reverse=True)


class TestAuditLogAccess:
    """测试审计日志访问记录"""
    
    def test_audit_log_access_is_logged(self, db_session, admin_token, sample_audit_logs):
        """测试审计日志访问本身也被记录"""
        # 获取访问前的日志数量
        initial_count = db_session.query(AuditLog).count()
        
        # 访问审计日志
        response = client.get(
            "/api/audit/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # 检查是否新增了审计日志
        final_count = db_session.query(AuditLog).count()
        assert final_count > initial_count
        
        # 检查新增的日志是否记录了审计日志访问
        latest_log = db_session.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
        assert latest_log.event_type == "authorization"
        assert latest_log.resource == "audit_logs"
        assert latest_log.action == "read"
        assert latest_log.success is True
    
    def test_security_events_access_is_logged(self, db_session, admin_token, sample_audit_logs):
        """测试安全事件访问被记录"""
        # 获取访问前的日志数量
        initial_count = db_session.query(AuditLog).count()
        
        # 访问安全事件
        response = client.get(
            "/api/audit/security-events",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # 检查是否新增了审计日志
        final_count = db_session.query(AuditLog).count()
        assert final_count > initial_count
        
        # 检查新增的日志是否记录了安全事件访问
        latest_log = db_session.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
        assert latest_log.event_type == "authorization"
        assert latest_log.resource == "security_events"
        assert latest_log.action == "read"
        assert latest_log.success is True


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_get_logs_with_no_results(self, db_session, admin_token):
        """测试没有匹配结果的查询"""
        response = client.get(
            "/api/audit/logs?user_id=nonexistent",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["logs"]) == 0
    
    def test_get_security_events_with_no_results(self, db_session, admin_token):
        """测试没有安全事件的情况"""
        response = client.get(
            "/api/audit/security-events?severity=low",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["events"]) == 0
    
    def test_get_logs_with_large_page_number(self, db_session, admin_token, sample_audit_logs):
        """测试超出范围的页码"""
        response = client.get(
            "/api/audit/logs?page=1000&page_size=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 0
        assert data["total"] == len(sample_audit_logs)
    
    def test_get_logs_with_max_page_size(self, db_session, admin_token, sample_audit_logs):
        """测试最大页面大小"""
        response = client.get(
            "/api/audit/logs?page_size=200",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 200
