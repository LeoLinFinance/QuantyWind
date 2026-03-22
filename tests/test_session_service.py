"""
会话管理服务单元测试
测试会话创建、验证、更新和终止功能
"""
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from redis import Redis

from backend.services.session_service import (
    SessionService,
    Session,
    SessionError,
    SessionExpiredError,
    SessionAnomalyError,
    MaxSessionsExceededError,
    get_session_service
)


@pytest.fixture
def mock_redis():
    """创建 Mock Redis 客户端"""
    redis_mock = Mock(spec=Redis)
    redis_mock.data = {}  # 模拟 Redis 数据存储
    redis_mock.sets = {}  # 模拟 Redis 集合存储
    
    def setex_side_effect(key, ttl, value):
        redis_mock.data[key] = value
        return True
    
    def get_side_effect(key):
        return redis_mock.data.get(key)
    
    def delete_side_effect(key):
        if key in redis_mock.data:
            del redis_mock.data[key]
            return 1
        return 0
    
    def sadd_side_effect(key, *values):
        if key not in redis_mock.sets:
            redis_mock.sets[key] = set()
        redis_mock.sets[key].update(values)
        return len(values)
    
    def smembers_side_effect(key):
        return redis_mock.sets.get(key, set())
    
    def srem_side_effect(key, *values):
        if key in redis_mock.sets:
            redis_mock.sets[key].discard(*values)
            return len(values)
        return 0
    
    redis_mock.setex.side_effect = setex_side_effect
    redis_mock.get.side_effect = get_side_effect
    redis_mock.delete.side_effect = delete_side_effect
    redis_mock.sadd.side_effect = sadd_side_effect
    redis_mock.smembers.side_effect = smembers_side_effect
    redis_mock.srem.side_effect = srem_side_effect
    
    return redis_mock


@pytest.fixture
def session_service(mock_redis):
    """创建会话服务实例"""
    return SessionService(redis_client=mock_redis)


class TestSessionCreation:
    """测试会话创建功能"""
    
    def test_create_session_success(self, session_service):
        """测试成功创建会话"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        assert session is not None
        assert session.id is not None
        assert session.user_id == user_id
        assert session.ip_address == ip_address
        assert session.user_agent == user_agent
        assert session.is_active is True
        assert session.created_at is not None
        assert session.last_activity is not None
        assert session.expires_at is not None
    
    def test_create_session_generates_unique_ids(self, session_service):
        """测试每次创建会话生成唯一 ID"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session1 = session_service.create_session(user_id, ip_address, user_agent)
        session2 = session_service.create_session(user_id, ip_address, user_agent)
        
        assert session1.id != session2.id
        assert session1.token != session2.token
    
    def test_create_session_sets_expiration(self, session_service):
        """测试会话创建时设置正确的过期时间"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        before_creation = datetime.utcnow()
        session = session_service.create_session(user_id, ip_address, user_agent)
        after_creation = datetime.utcnow()
        
        expected_expiration = before_creation + timedelta(
            minutes=SessionService.SESSION_TIMEOUT_MINUTES
        )
        
        # 允许几秒的误差
        assert abs((session.expires_at - expected_expiration).total_seconds()) < 5
    
    def test_create_session_stores_in_redis(self, session_service, mock_redis):
        """测试会话数据正确存储到 Redis"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 验证 setex 被调用
        mock_redis.setex.assert_called()
        
        # 验证数据被存储
        session_key = f"session:{session.id}"
        assert session_key in mock_redis.data
        
        # 验证存储的数据格式正确
        stored_data = json.loads(mock_redis.data[session_key])
        assert stored_data["id"] == session.id
        assert stored_data["user_id"] == user_id
    
    def test_create_session_adds_to_user_sessions(self, session_service, mock_redis):
        """测试会话 ID 被添加到用户会话列表"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 验证 sadd 被调用
        mock_redis.sadd.assert_called()
        
        # 验证会话 ID 在用户会话集合中
        user_sessions_key = f"user_sessions:{user_id}"
        assert session.id in mock_redis.sets[user_sessions_key]


class TestSessionValidation:
    """测试会话验证功能"""
    
    def test_validate_session_success(self, session_service):
        """测试有效会话验证成功"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 验证会话应该成功
        result = session_service.validate_session(session.id, ip_address)
        assert result is True
    
    def test_validate_session_not_found(self, session_service):
        """测试不存在的会话验证失败"""
        with pytest.raises(SessionExpiredError):
            session_service.validate_session("nonexistent_session", "192.168.1.100")
    
    def test_validate_session_ip_mismatch(self, session_service):
        """测试 IP 地址不匹配时验证失败"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 使用不同的 IP 地址验证
        with pytest.raises(SessionAnomalyError) as exc_info:
            session_service.validate_session(session.id, "192.168.1.200")
        
        assert "IP address mismatch" in str(exc_info.value)
    
    def test_validate_session_expired(self, session_service, mock_redis):
        """测试过期会话验证失败"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 修改会话使其过期
        session_data = json.loads(mock_redis.data[f"session:{session.id}"])
        expired_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        session_data["expires_at"] = expired_time
        mock_redis.data[f"session:{session.id}"] = json.dumps(session_data)
        
        # 验证应该失败
        with pytest.raises(SessionExpiredError):
            session_service.validate_session(session.id, ip_address)
    
    def test_validate_session_inactive(self, session_service, mock_redis):
        """测试非活动会话验证失败"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 修改会话为非活动状态
        session_data = json.loads(mock_redis.data[f"session:{session.id}"])
        session_data["is_active"] = False
        mock_redis.data[f"session:{session.id}"] = json.dumps(session_data)
        
        # 验证应该失败
        with pytest.raises(SessionExpiredError):
            session_service.validate_session(session.id, ip_address)


class TestSessionActivity:
    """测试会话活动更新功能"""
    
    def test_update_activity_success(self, session_service, mock_redis):
        """测试成功更新会话活动时间"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        original_activity = session.last_activity
        
        # 等待一小段时间
        import time
        time.sleep(0.1)
        
        # 更新活动时间
        result = session_service.update_activity(session.id)
        assert result is True
        
        # 获取更新后的会话
        updated_session = session_service.get_session(session.id)
        assert updated_session.last_activity > original_activity
    
    def test_update_activity_extends_expiration(self, session_service, mock_redis):
        """测试更新活动时间延长过期时间"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        original_expiration = session.expires_at
        
        # 等待一小段时间
        import time
        time.sleep(0.1)
        
        # 更新活动时间
        session_service.update_activity(session.id)
        
        # 获取更新后的会话
        updated_session = session_service.get_session(session.id)
        assert updated_session.expires_at > original_expiration
    
    def test_update_activity_nonexistent_session(self, session_service):
        """测试更新不存在的会话返回 False"""
        result = session_service.update_activity("nonexistent_session")
        assert result is False


class TestSessionTermination:
    """测试会话终止功能"""
    
    def test_terminate_session_success(self, session_service, mock_redis):
        """测试成功终止会话"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 终止会话
        result = session_service.terminate_session(session.id)
        assert result is True
        
        # 验证会话已被删除
        assert session_service.get_session(session.id) is None
    
    def test_terminate_session_removes_from_user_sessions(self, session_service, mock_redis):
        """测试终止会话从用户会话列表中移除"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        user_sessions_key = f"user_sessions:{user_id}"
        
        # 验证会话在列表中
        assert session.id in mock_redis.sets[user_sessions_key]
        
        # 终止会话
        session_service.terminate_session(session.id)
        
        # 验证会话已从列表中移除
        assert session.id not in mock_redis.sets.get(user_sessions_key, set())
    
    def test_terminate_nonexistent_session(self, session_service):
        """测试终止不存在的会话返回 False"""
        result = session_service.terminate_session("nonexistent_session")
        assert result is False


class TestMultipleSessionsManagement:
    """测试多会话管理功能"""
    
    def test_get_active_sessions(self, session_service):
        """测试获取用户的所有活动会话"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        # 创建多个会话
        session1 = session_service.create_session(user_id, ip_address, user_agent)
        session2 = session_service.create_session(user_id, ip_address, user_agent)
        
        # 获取活动会话
        active_sessions = session_service.get_active_sessions(user_id)
        
        assert len(active_sessions) == 2
        session_ids = [s.id for s in active_sessions]
        assert session1.id in session_ids
        assert session2.id in session_ids
    
    def test_max_sessions_limit(self, session_service):
        """测试最大会话数限制"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        # 创建最大数量的会话
        sessions = []
        for i in range(SessionService.MAX_SESSIONS_PER_USER):
            session = session_service.create_session(user_id, ip_address, user_agent)
            sessions.append(session)
        
        # 创建第 4 个会话应该删除最旧的会话
        new_session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 验证只有 3 个活动会话
        active_sessions = session_service.get_active_sessions(user_id)
        assert len(active_sessions) == SessionService.MAX_SESSIONS_PER_USER
        
        # 验证最旧的会话被删除
        session_ids = [s.id for s in active_sessions]
        assert sessions[0].id not in session_ids
        assert new_session.id in session_ids
    
    def test_terminate_all_user_sessions(self, session_service):
        """测试终止用户的所有会话"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        # 创建多个会话
        session_service.create_session(user_id, ip_address, user_agent)
        session_service.create_session(user_id, ip_address, user_agent)
        session_service.create_session(user_id, ip_address, user_agent)
        
        # 终止所有会话
        count = session_service.terminate_all_user_sessions(user_id)
        
        assert count == 3
        
        # 验证没有活动会话
        active_sessions = session_service.get_active_sessions(user_id)
        assert len(active_sessions) == 0


class TestSessionSerialization:
    """测试会话序列化和反序列化"""
    
    def test_session_to_dict(self):
        """测试会话对象转换为字典"""
        now = datetime.utcnow()
        session = Session(
            id="session_123",
            user_id="user_123",
            token="token_abc",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            created_at=now,
            last_activity=now,
            expires_at=now + timedelta(minutes=30),
            is_active=True
        )
        
        session_dict = session.to_dict()
        
        assert session_dict["id"] == "session_123"
        assert session_dict["user_id"] == "user_123"
        assert session_dict["token"] == "token_abc"
        assert session_dict["ip_address"] == "192.168.1.100"
        assert session_dict["is_active"] is True
    
    def test_session_from_dict(self):
        """测试从字典创建会话对象"""
        now = datetime.utcnow()
        session_dict = {
            "id": "session_123",
            "user_id": "user_123",
            "token": "token_abc",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "created_at": now.isoformat(),
            "last_activity": now.isoformat(),
            "expires_at": (now + timedelta(minutes=30)).isoformat(),
            "is_active": True
        }
        
        session = Session.from_dict(session_dict)
        
        assert session.id == "session_123"
        assert session.user_id == "user_123"
        assert session.token == "token_abc"
        assert session.is_active is True


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_empty_user_id(self, session_service):
        """测试空用户 ID"""
        session = session_service.create_session("", "192.168.1.100", "Mozilla/5.0")
        assert session.user_id == ""
    
    def test_empty_ip_address(self, session_service):
        """测试空 IP 地址"""
        session = session_service.create_session("user_123", "", "Mozilla/5.0")
        assert session.ip_address == ""
    
    def test_empty_user_agent(self, session_service):
        """测试空 User-Agent"""
        session = session_service.create_session("user_123", "192.168.1.100", "")
        assert session.user_agent == ""
    
    def test_very_long_user_agent(self, session_service):
        """测试超长 User-Agent"""
        long_user_agent = "A" * 10000
        session = session_service.create_session("user_123", "192.168.1.100", long_user_agent)
        assert session.user_agent == long_user_agent
    
    def test_corrupted_session_data(self, session_service, mock_redis):
        """测试损坏的会话数据"""
        user_id = "user_123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        session = session_service.create_session(user_id, ip_address, user_agent)
        
        # 损坏会话数据
        session_key = f"session:{session.id}"
        mock_redis.data[session_key] = "invalid json data"
        
        # 获取会话应该返回 None
        result = session_service.get_session(session.id)
        assert result is None


class TestGetSessionService:
    """测试全局会话服务获取函数"""
    
    def test_get_session_service_singleton(self):
        """测试获取会话服务返回单例"""
        service1 = get_session_service()
        service2 = get_session_service()
        
        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
