"""
审计日志服务单元测试
测试审计日志记录、查询和管理功能
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.models.audit_log import AuditLog
from backend.database.config import Base
from backend.services.audit_log_service import AuditLogService


# 创建内存数据库用于测试
@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def audit_service(db_session):
    """创建审计日志服务实例"""
    return AuditLogService(db_session)


class TestAuthenticationLogging:
    """测试身份验证事件日志记录"""
    
    def test_log_successful_login(self, audit_service):
        """测试记录成功登录"""
        log = audit_service.log_authentication(
            user_id="user_123",
            action="login",
            success=True,
            ip_address="192.168.1.100",
            details={"user_agent": "Mozilla/5.0", "session_id": "sess_xyz"}
        )
        
        assert log.id is not None
        assert log.event_type == "authentication"
        assert log.action == "login"
        assert log.user_id == "user_123"
        assert log.ip_address == "192.168.1.100"
        assert log.success is True
        assert log.severity == "info"
        assert log.details["user_agent"] == "Mozilla/5.0"
        assert log.timestamp is not None
    
    def test_log_failed_login(self, audit_service):
        """测试记录失败登录"""
        log = audit_service.log_authentication(
            user_id="user_123",
            action="login",
            success=False,
            ip_address="192.168.1.100",
            details={"failure_reason": "invalid_password"}
        )
        
        assert log.success is False
        assert log.severity == "medium"  # 失败登录应该有更高的严重程度
        assert log.details["failure_reason"] == "invalid_password"
    
    def test_log_logout(self, audit_service):
        """测试记录登出"""
        log = audit_service.log_authentication(
            user_id="user_123",
            action="logout",
            success=True,
            ip_address="192.168.1.100"
        )
        
        assert log.action == "logout"
        assert log.success is True
    
    def test_log_token_refresh(self, audit_service):
        """测试记录令牌刷新"""
        log = audit_service.log_authentication(
            user_id="user_123",
            action="token_refresh",
            success=True,
            ip_address="192.168.1.100",
            details={"old_token_id": "token_abc", "new_token_id": "token_xyz"}
        )
        
        assert log.action == "token_refresh"
        assert log.details["old_token_id"] == "token_abc"
    
    def test_log_registration(self, audit_service):
        """测试记录用户注册"""
        log = audit_service.log_authentication(
            user_id=None,  # 注册时可能还没有 ID
            action="register",
            success=True,
            ip_address="192.168.1.100",
            details={"username": "newuser", "email": "newuser@example.com"}
        )
        
        assert log.action == "register"
        assert log.user_id is None
        assert log.details["username"] == "newuser"


class TestAuthorizationLogging:
    """测试授权检查日志记录"""
    
    def test_log_granted_authorization(self, audit_service):
        """测试记录授权成功"""
        log = audit_service.log_authorization(
            user_id="user_123",
            resource="portfolio",
            action="read",
            granted=True
        )
        
        assert log.event_type == "authorization"
        assert log.action == "read_portfolio"
        assert log.resource == "portfolio"
        assert log.success is True
        assert log.severity == "info"
    
    def test_log_denied_authorization(self, audit_service):
        """测试记录授权拒绝"""
        log = audit_service.log_authorization(
            user_id="user_123",
            resource="user_management",
            action="write",
            granted=False,
            reason="insufficient_permissions"
        )
        
        assert log.success is False
        assert log.severity == "medium"  # 拒绝的授权应该有更高的严重程度
        assert log.details["reason"] == "insufficient_permissions"
    
    def test_log_authorization_without_reason(self, audit_service):
        """测试记录授权（不提供原因）"""
        log = audit_service.log_authorization(
            user_id="user_123",
            resource="market_data",
            action="read",
            granted=True
        )
        
        assert log.details == {}


class TestSecurityEventLogging:
    """测试安全事件日志记录"""
    
    def test_log_account_locked(self, audit_service):
        """测试记录账户锁定事件"""
        log = audit_service.log_security_event(
            event_type="account_locked",
            severity="high",
            description="Account locked due to 5 failed login attempts",
            metadata={"failed_attempts": 5, "lock_duration": "15 minutes"},
            user_id="user_123",
            ip_address="192.168.1.100"
        )
        
        assert log.event_type == "security_event"
        assert log.action == "account_locked"
        assert log.severity == "high"
        assert log.success is False
        assert log.details["description"] == "Account locked due to 5 failed login attempts"
        assert log.details["failed_attempts"] == 5
    
    def test_log_intrusion_attempt(self, audit_service):
        """测试记录入侵尝试"""
        log = audit_service.log_security_event(
            event_type="intrusion_attempt",
            severity="critical",
            description="SQL injection attempt detected",
            metadata={"attack_type": "sql_injection", "payload": "' OR '1'='1"},
            ip_address="192.168.1.200"
        )
        
        assert log.severity == "critical"
        assert log.details["attack_type"] == "sql_injection"
    
    def test_log_session_hijack(self, audit_service):
        """测试记录会话劫持尝试"""
        log = audit_service.log_security_event(
            event_type="session_hijack",
            severity="high",
            description="IP address changed during active session",
            metadata={"old_ip": "192.168.1.100", "new_ip": "192.168.1.200"},
            user_id="user_123"
        )
        
        assert log.action == "session_hijack"
        assert log.details["old_ip"] == "192.168.1.100"
    
    def test_invalid_severity_defaults_to_medium(self, audit_service):
        """测试无效的严重程度默认为 medium"""
        log = audit_service.log_security_event(
            event_type="test_event",
            severity="invalid_severity",
            description="Test event"
        )
        
        assert log.severity == "medium"


class TestLogQuerying:
    """测试日志查询功能"""
    
    def test_query_logs_by_event_type(self, audit_service):
        """测试按事件类型查询"""
        # 创建测试数据
        audit_service.log_authentication("user_1", "login", True, "192.168.1.1")
        audit_service.log_authentication("user_2", "login", False, "192.168.1.2")
        audit_service.log_authorization("user_1", "portfolio", "read", True)
        
        # 查询认证事件
        logs = audit_service.query_logs(filters={"event_type": "authentication"})
        
        assert len(logs) == 2
        assert all(log.event_type == "authentication" for log in logs)
    
    def test_query_logs_by_user_id(self, audit_service):
        """测试按用户 ID 查询"""
        audit_service.log_authentication("user_1", "login", True, "192.168.1.1")
        audit_service.log_authentication("user_2", "login", True, "192.168.1.2")
        audit_service.log_authorization("user_1", "portfolio", "read", True)
        
        logs = audit_service.query_logs(filters={"user_id": "user_1"})
        
        assert len(logs) == 2
        assert all(log.user_id == "user_1" for log in logs)
    
    def test_query_logs_by_success(self, audit_service):
        """测试按成功状态查询"""
        audit_service.log_authentication("user_1", "login", True, "192.168.1.1")
        audit_service.log_authentication("user_2", "login", False, "192.168.1.2")
        audit_service.log_authentication("user_3", "login", False, "192.168.1.3")
        
        failed_logs = audit_service.query_logs(filters={"success": False})
        
        assert len(failed_logs) == 2
        assert all(log.success is False for log in failed_logs)
    
    def test_query_logs_by_time_range(self, audit_service):
        """测试按时间范围查询"""
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # 创建不同时间的日志（通过直接操作数据库）
        log1 = AuditLog(
            event_type="authentication",
            action="login",
            user_id="user_1",
            ip_address="192.168.1.1",
            success=True,
            severity="info",
            timestamp=now - timedelta(hours=2)
        )
        log2 = AuditLog(
            event_type="authentication",
            action="login",
            user_id="user_2",
            ip_address="192.168.1.2",
            success=True,
            severity="info",
            timestamp=now - timedelta(minutes=30)
        )
        
        audit_service.db.add(log1)
        audit_service.db.add(log2)
        audit_service.db.commit()
        
        # 查询最近 1 小时的日志
        logs = audit_service.query_logs(
            start_time=now - timedelta(hours=1)
        )
        
        assert len(logs) == 1
        assert logs[0].user_id == "user_2"
    
    def test_query_logs_with_pagination(self, audit_service):
        """测试分页查询"""
        # 创建 10 条日志
        for i in range(10):
            audit_service.log_authentication(
                f"user_{i}",
                "login",
                True,
                "192.168.1.1"
            )
        
        # 第一页（前 5 条）
        page1 = audit_service.query_logs(limit=5, offset=0)
        assert len(page1) == 5
        
        # 第二页（后 5 条）
        page2 = audit_service.query_logs(limit=5, offset=5)
        assert len(page2) == 5
        
        # 确保没有重复
        page1_ids = {log.id for log in page1}
        page2_ids = {log.id for log in page2}
        assert len(page1_ids & page2_ids) == 0
    
    def test_query_logs_ordered_by_timestamp(self, audit_service):
        """测试日志按时间倒序排列"""
        audit_service.log_authentication("user_1", "login", True, "192.168.1.1")
        audit_service.log_authentication("user_2", "login", True, "192.168.1.2")
        audit_service.log_authentication("user_3", "login", True, "192.168.1.3")
        
        logs = audit_service.query_logs()
        
        # 验证按时间倒序
        for i in range(len(logs) - 1):
            assert logs[i].timestamp >= logs[i + 1].timestamp


class TestFailedLoginTracking:
    """测试失败登录追踪"""
    
    def test_get_failed_login_attempts_by_user(self, audit_service):
        """测试获取用户的失败登录次数"""
        # 创建失败登录记录
        for i in range(3):
            audit_service.log_authentication(
                "user_123",
                "login",
                False,
                "192.168.1.100"
            )
        
        # 创建成功登录记录（不应计入）
        audit_service.log_authentication(
            "user_123",
            "login",
            True,
            "192.168.1.100"
        )
        
        count = audit_service.get_failed_login_attempts(user_id="user_123")
        
        assert count == 3
    
    def test_get_failed_login_attempts_by_ip(self, audit_service):
        """测试获取 IP 地址的失败登录次数"""
        audit_service.log_authentication("user_1", "login", False, "192.168.1.100")
        audit_service.log_authentication("user_2", "login", False, "192.168.1.100")
        audit_service.log_authentication("user_3", "login", False, "192.168.1.200")
        
        count = audit_service.get_failed_login_attempts(ip_address="192.168.1.100")
        
        assert count == 2
    
    def test_failed_login_attempts_time_window(self, audit_service, db_session):
        """测试失败登录时间窗口"""
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # 创建旧的失败登录（超出时间窗口）
        old_log = AuditLog(
            event_type="authentication",
            action="login",
            user_id="user_123",
            ip_address="192.168.1.100",
            success=False,
            severity="medium",
            timestamp=now - timedelta(minutes=20)
        )
        db_session.add(old_log)
        db_session.commit()  # 提交旧日志
        
        # 创建新的失败登录（在时间窗口内）
        audit_service.log_authentication(
            "user_123",
            "login",
            False,
            "192.168.1.100"
        )
        
        # 查询最近 15 分钟的失败登录
        count = audit_service.get_failed_login_attempts(
            user_id="user_123",
            time_window=timedelta(minutes=15)
        )
        
        assert count == 1  # 只计入时间窗口内的


class TestSecurityEventRetrieval:
    """测试安全事件检索"""
    
    def test_get_security_events(self, audit_service):
        """测试获取安全事件"""
        audit_service.log_security_event(
            "intrusion_attempt",
            "critical",
            "SQL injection detected"
        )
        audit_service.log_security_event(
            "account_locked",
            "high",
            "Account locked"
        )
        audit_service.log_authentication("user_1", "login", True, "192.168.1.1")
        
        events = audit_service.get_security_events()
        
        assert len(events) == 2
        assert all(event.event_type == "security_event" for event in events)
    
    def test_get_security_events_by_severity(self, audit_service):
        """测试按严重程度获取安全事件"""
        audit_service.log_security_event("event1", "critical", "Critical event")
        audit_service.log_security_event("event2", "high", "High event")
        audit_service.log_security_event("event3", "medium", "Medium event")
        
        critical_events = audit_service.get_security_events(severity="critical")
        
        assert len(critical_events) == 1
        assert critical_events[0].severity == "critical"


class TestUserActivityTracking:
    """测试用户活动追踪"""
    
    def test_get_user_activity(self, audit_service):
        """测试获取用户活动"""
        audit_service.log_authentication("user_123", "login", True, "192.168.1.1")
        audit_service.log_authorization("user_123", "portfolio", "read", True)
        audit_service.log_authorization("user_123", "market_data", "write", False)
        audit_service.log_authentication("user_456", "login", True, "192.168.1.2")
        
        activity = audit_service.get_user_activity("user_123")
        
        assert len(activity) == 3
        assert all(log.user_id == "user_123" for log in activity)


class TestLogCleanup:
    """测试日志清理"""
    
    def test_cleanup_old_logs(self, audit_service, db_session):
        """测试清理旧日志"""
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # 创建旧日志（超过 90 天）
        old_log = AuditLog(
            event_type="authentication",
            action="login",
            user_id="user_old",
            ip_address="192.168.1.1",
            success=True,
            severity="info",
            timestamp=now - timedelta(days=100)
        )
        db_session.add(old_log)
        
        # 创建新日志
        audit_service.log_authentication("user_new", "login", True, "192.168.1.2")
        
        # 清理旧日志
        deleted_count = audit_service.cleanup_old_logs(retention_days=90)
        
        assert deleted_count == 1
        
        # 验证新日志仍然存在
        remaining_logs = audit_service.query_logs()
        assert len(remaining_logs) == 1
        assert remaining_logs[0].user_id == "user_new"


class TestStatistics:
    """测试统计功能"""
    
    def test_get_statistics(self, audit_service):
        """测试获取统计信息"""
        # 创建各种类型的日志
        audit_service.log_authentication("user_1", "login", True, "192.168.1.1")
        audit_service.log_authentication("user_2", "login", False, "192.168.1.2")
        audit_service.log_authorization("user_1", "portfolio", "read", True)
        audit_service.log_authorization("user_2", "admin", "write", False)
        audit_service.log_security_event("intrusion", "critical", "Attack detected")
        
        stats = audit_service.get_statistics()
        
        assert stats["total_events"] == 5
        assert stats["by_event_type"]["authentication"] == 2
        assert stats["by_event_type"]["authorization"] == 2
        assert stats["by_event_type"]["security_event"] == 1
        assert stats["failed_authentications"] == 1
        assert stats["denied_authorizations"] == 1
    
    def test_get_statistics_with_time_range(self, audit_service, db_session):
        """测试获取指定时间范围的统计信息"""
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # 创建旧日志
        old_log = AuditLog(
            event_type="authentication",
            action="login",
            user_id="user_old",
            ip_address="192.168.1.1",
            success=True,
            severity="info",
            timestamp=now - timedelta(days=2)
        )
        db_session.add(old_log)
        
        # 创建新日志
        audit_service.log_authentication("user_new", "login", True, "192.168.1.2")
        
        # 获取最近 1 天的统计
        stats = audit_service.get_statistics(
            start_time=now - timedelta(days=1)
        )
        
        assert stats["total_events"] == 1


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_log_with_empty_details(self, audit_service):
        """测试空详情"""
        log = audit_service.log_authentication(
            "user_123",
            "login",
            True,
            "192.168.1.1",
            details=None
        )
        
        assert log.details == {}
    
    def test_log_with_none_user_id(self, audit_service):
        """测试 None 用户 ID"""
        log = audit_service.log_authentication(
            None,
            "register",
            True,
            "192.168.1.1"
        )
        
        assert log.user_id is None
    
    def test_query_with_no_filters(self, audit_service):
        """测试无过滤条件查询"""
        audit_service.log_authentication("user_1", "login", True, "192.168.1.1")
        
        logs = audit_service.query_logs()
        
        assert len(logs) >= 1
    
    def test_query_with_empty_result(self, audit_service):
        """测试空结果查询"""
        logs = audit_service.query_logs(filters={"user_id": "nonexistent"})
        
        assert len(logs) == 0
