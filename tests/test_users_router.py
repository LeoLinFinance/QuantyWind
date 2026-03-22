"""
用户管理路由测试

测试用户管理 API 端点的功能和权限控制
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.main import app
from backend.database.config import Base, get_db
from backend.models.user import User
from backend.services.authentication_service import get_authentication_service
from backend.services.encryption_service import get_encryption_service


# 测试数据库设置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_users_router.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def encryption_service():
    """获取加密服务"""
    return get_encryption_service()


@pytest.fixture
def auth_service():
    """获取认证服务"""
    return get_authentication_service()


@pytest.fixture
def admin_user(db, encryption_service):
    """创建管理员用户"""
    user = User(
        username="admin",
        email="admin@test.com",
        password_hash=encryption_service.hash_password("Admin123!"),
        role="admin",
        is_active=True,
        is_locked=False,
        failed_login_attempts=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db, encryption_service):
    """创建普通用户"""
    user = User(
        username="user",
        email="user@test.com",
        password_hash=encryption_service.hash_password("User123!"),
        role="user",
        is_active=True,
        is_locked=False,
        failed_login_attempts=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def viewer_user(db, encryption_service):
    """创建查看者用户"""
    user = User(
        username="viewer",
        email="viewer@test.com",
        password_hash=encryption_service.hash_password("Viewer123!"),
        role="viewer",
        is_active=True,
        is_locked=False,
        failed_login_attempts=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user, auth_service, db):
    """生成管理员令牌"""
    auth_token = auth_service.authenticate("admin", "Admin123!", db)
    return auth_token.access_token


@pytest.fixture
def user_token(regular_user, auth_service, db):
    """生成普通用户令牌"""
    auth_token = auth_service.authenticate("user", "User123!", db)
    return auth_token.access_token


@pytest.fixture
def viewer_token(viewer_user, auth_service, db):
    """生成查看者令牌"""
    auth_token = auth_service.authenticate("viewer", "Viewer123!", db)
    return auth_token.access_token


class TestGetUsers:
    """测试获取用户列表端点"""
    
    def test_get_users_as_admin(self, client, admin_token, admin_user, regular_user, viewer_user):
        """管理员可以获取用户列表"""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] >= 3  # 至少有 3 个用户
        assert len(data["users"]) >= 3
    
    def test_get_users_with_pagination(self, client, admin_token, db, encryption_service):
        """测试分页功能"""
        # 创建额外的用户
        for i in range(5):
            user = User(
                username=f"testuser{i}",
                email=f"testuser{i}@test.com",
                password_hash=encryption_service.hash_password("Test123!"),
                role="user",
                is_active=True,
                is_locked=False,
                failed_login_attempts=0
            )
            db.add(user)
        db.commit()
        
        # 测试第一页
        response = client.get(
            "/api/users?page=1&page_size=3",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 3
        assert len(data["users"]) == 3
        assert data["total"] >= 8
    
    def test_get_users_with_role_filter(self, client, admin_token, admin_user, regular_user):
        """测试按角色过滤"""
        response = client.get(
            "/api/users?role=admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(user["role"] == "admin" for user in data["users"])
    
    def test_get_users_as_regular_user(self, client, user_token):
        """普通用户无法获取用户列表"""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
        assert "管理员权限" in response.json()["detail"]
    
    def test_get_users_without_auth(self, client):
        """未认证用户无法获取用户列表"""
        response = client.get("/api/users")
        
        assert response.status_code == 403


class TestGetUser:
    """测试获取用户详情端点"""
    
    def test_get_user_as_admin(self, client, admin_token, regular_user):
        """管理员可以获取任何用户的详情"""
        response = client.get(
            f"/api/users/{regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == regular_user.id
        assert data["username"] == regular_user.username
        assert data["email"] == regular_user.email
        assert data["role"] == regular_user.role
    
    def test_get_self_as_regular_user(self, client, user_token, regular_user):
        """普通用户可以获取自己的详情"""
        response = client.get(
            f"/api/users/{regular_user.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == regular_user.id
        assert data["username"] == regular_user.username
    
    def test_get_other_user_as_regular_user(self, client, user_token, admin_user):
        """普通用户无法获取其他用户的详情"""
        response = client.get(
            f"/api/users/{admin_user.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
        assert "只能查看自己" in response.json()["detail"]
    
    def test_get_nonexistent_user(self, client, admin_token):
        """获取不存在的用户返回 404"""
        response = client.get(
            "/api/users/nonexistent-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]


class TestUpdateUserRole:
    """测试更新用户角色端点"""
    
    def test_update_role_as_admin(self, client, admin_token, regular_user, db):
        """管理员可以更新用户角色"""
        response = client.put(
            f"/api/users/{regular_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "admin"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["role"] == "admin"
        
        # 验证数据库中的角色已更新
        db.refresh(regular_user)
        assert regular_user.role == "admin"
    
    def test_update_role_to_viewer(self, client, admin_token, regular_user, db):
        """测试将用户角色更新为 viewer"""
        response = client.put(
            f"/api/users/{regular_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "viewer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "viewer"
    
    def test_update_role_with_invalid_role(self, client, admin_token, regular_user):
        """使用无效角色更新失败"""
        response = client.put(
            f"/api/users/{regular_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "superadmin"}
        )
        
        assert response.status_code == 400
        assert "无效的角色" in response.json()["detail"]
    
    def test_update_own_role(self, client, admin_token, admin_user):
        """管理员不能修改自己的角色"""
        response = client.put(
            f"/api/users/{admin_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "user"}
        )
        
        assert response.status_code == 400
        assert "不能修改自己的角色" in response.json()["detail"]
    
    def test_update_role_as_regular_user(self, client, user_token, viewer_user):
        """普通用户无法更新角色"""
        response = client.put(
            f"/api/users/{viewer_user.id}/role",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"role": "admin"}
        )
        
        assert response.status_code == 403
        assert "管理员权限" in response.json()["detail"]
    
    def test_update_nonexistent_user_role(self, client, admin_token):
        """更新不存在的用户角色返回 404"""
        response = client.put(
            "/api/users/nonexistent-id/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "admin"}
        )
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]


class TestDeleteUser:
    """测试删除用户端点"""
    
    def test_delete_user_as_admin(self, client, admin_token, regular_user, db):
        """管理员可以删除用户（软删除）"""
        response = client.delete(
            f"/api/users/{regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "停用" in data["message"]
        
        # 验证用户被标记为非激活
        db.refresh(regular_user)
        assert regular_user.is_active is False
    
    def test_delete_self(self, client, admin_token, admin_user):
        """管理员不能删除自己"""
        response = client.delete(
            f"/api/users/{admin_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "不能删除自己" in response.json()["detail"]
    
    def test_delete_user_as_regular_user(self, client, user_token, viewer_user):
        """普通用户无法删除用户"""
        response = client.delete(
            f"/api/users/{viewer_user.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
        assert "管理员权限" in response.json()["detail"]
    
    def test_delete_nonexistent_user(self, client, admin_token):
        """删除不存在的用户返回 404"""
        response = client.delete(
            "/api/users/nonexistent-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]


class TestAuditLogging:
    """测试审计日志记录"""
    
    def test_user_list_access_logged(self, client, admin_token, db):
        """验证用户列表访问被记录"""
        from backend.models.audit_log import AuditLog
        
        # 执行操作
        client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # 检查审计日志
        logs = db.query(AuditLog).filter(
            AuditLog.event_type == "authorization",
            AuditLog.resource == "user_management",
            AuditLog.action == "read"
        ).all()
        
        assert len(logs) > 0
        assert logs[-1].success is True
    
    def test_role_update_logged(self, client, admin_token, regular_user, db):
        """验证角色更新被记录"""
        from backend.models.audit_log import AuditLog
        
        # 执行操作
        client.put(
            f"/api/users/{regular_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "viewer"}
        )
        
        # 检查安全事件日志
        logs = db.query(AuditLog).filter(
            AuditLog.event_type == "security_event",
            AuditLog.action == "role_changed"
        ).all()
        
        assert len(logs) > 0
        assert logs[-1].severity == "medium"
    
    def test_user_deletion_logged(self, client, admin_token, regular_user, db):
        """验证用户删除被记录"""
        from backend.models.audit_log import AuditLog
        
        # 执行操作
        client.delete(
            f"/api/users/{regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # 检查安全事件日志
        logs = db.query(AuditLog).filter(
            AuditLog.event_type == "security_event",
            AuditLog.action == "user_deleted"
        ).all()
        
        assert len(logs) > 0
        assert logs[-1].severity == "high"
    
    def test_unauthorized_access_logged(self, client, user_token, admin_user, db):
        """验证未授权访问尝试被记录"""
        from backend.models.audit_log import AuditLog
        
        # 执行操作（应该失败）
        client.get(
            f"/api/users/{admin_user.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # 检查审计日志
        logs = db.query(AuditLog).filter(
            AuditLog.event_type == "authorization",
            AuditLog.success == False
        ).all()
        
        assert len(logs) > 0


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_get_users_with_invalid_page(self, client, admin_token):
        """测试无效的页码"""
        response = client.get(
            "/api/users?page=0",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # FastAPI 的查询参数验证会返回 422
        assert response.status_code == 422
    
    def test_get_users_with_large_page_size(self, client, admin_token):
        """测试超大的页面大小"""
        response = client.get(
            "/api/users?page_size=1000",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # 应该被限制在最大值 100
        assert response.status_code == 422
    
    def test_update_role_with_empty_role(self, client, admin_token, regular_user):
        """测试空角色"""
        response = client.put(
            f"/api/users/{regular_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": ""}
        )
        
        assert response.status_code == 400
    
    def test_concurrent_role_updates(self, client, admin_token, regular_user, db):
        """测试并发角色更新"""
        # 第一次更新
        response1 = client.put(
            f"/api/users/{regular_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "viewer"}
        )
        
        # 第二次更新
        response2 = client.put(
            f"/api/users/{regular_user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "admin"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # 验证最终状态
        db.refresh(regular_user)
        assert regular_user.role == "admin"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
