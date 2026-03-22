"""
用户管理路由独立测试

不依赖完整应用，直接测试路由功能
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.config import Base, get_db
from backend.models.user import User
from backend.routers.users import router
from backend.services.authentication_service import get_authentication_service
from backend.services.encryption_service import get_encryption_service


# 测试数据库设置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_users_standalone.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 创建测试应用
app = FastAPI()
app.include_router(router)


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
def admin_token(admin_user, auth_service, db):
    """生成管理员令牌"""
    auth_token = auth_service.authenticate("admin", "Admin123!", db)
    return auth_token.access_token


@pytest.fixture
def user_token(regular_user, auth_service, db):
    """生成普通用户令牌"""
    auth_token = auth_service.authenticate("user", "User123!", db)
    return auth_token.access_token


def test_get_users_as_admin(client, admin_token, admin_user, regular_user):
    """管理员可以获取用户列表"""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert data["total"] >= 2


def test_get_users_as_regular_user(client, user_token):
    """普通用户无法获取用户列表"""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403


def test_get_user_as_admin(client, admin_token, regular_user):
    """管理员可以获取任何用户的详情"""
    response = client.get(
        f"/api/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == regular_user.id
    assert data["username"] == regular_user.username


def test_get_self_as_regular_user(client, user_token, regular_user):
    """普通用户可以获取自己的详情"""
    response = client.get(
        f"/api/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == regular_user.id


def test_update_role_as_admin(client, admin_token, regular_user, db):
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


def test_update_role_with_invalid_role(client, admin_token, regular_user):
    """使用无效角色更新失败"""
    response = client.put(
        f"/api/users/{regular_user.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "superadmin"}
    )
    
    assert response.status_code == 400


def test_delete_user_as_admin(client, admin_token, regular_user, db):
    """管理员可以删除用户（软删除）"""
    response = client.delete(
        f"/api/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # 验证用户被标记为非激活
    db.refresh(regular_user)
    assert regular_user.is_active is False


def test_delete_self(client, admin_token, admin_user):
    """管理员不能删除自己"""
    response = client.delete(
        f"/api/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
