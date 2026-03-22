"""
授权服务单元测试
测试基于角色的访问控制（RBAC）功能
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.config import Base
from backend.models.user import User
from backend.services.authorization_service import AuthorizationService, Permission


# 创建测试数据库
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_service(db_session):
    """创建授权服务实例"""
    return AuthorizationService(db_session)


@pytest.fixture
def test_users(db_session):
    """创建测试用户"""
    users = {
        "viewer": User(
            id="viewer-001",
            username="viewer_user",
            email="viewer@test.com",
            password_hash="hashed_password",
            role="viewer",
            is_active=True,
            is_locked=False
        ),
        "user": User(
            id="user-001",
            username="normal_user",
            email="user@test.com",
            password_hash="hashed_password",
            role="user",
            is_active=True,
            is_locked=False
        ),
        "admin": User(
            id="admin-001",
            username="admin_user",
            email="admin@test.com",
            password_hash="hashed_password",
            role="admin",
            is_active=True,
            is_locked=False
        ),
        "locked": User(
            id="locked-001",
            username="locked_user",
            email="locked@test.com",
            password_hash="hashed_password",
            role="user",
            is_active=True,
            is_locked=True
        ),
        "inactive": User(
            id="inactive-001",
            username="inactive_user",
            email="inactive@test.com",
            password_hash="hashed_password",
            role="user",
            is_active=False,
            is_locked=False
        )
    }
    
    for user in users.values():
        db_session.add(user)
    db_session.commit()
    
    return users


class TestPermissionCheck:
    """测试权限检查功能"""
    
    def test_viewer_can_read_portfolio(self, auth_service, test_users):
        """测试 viewer 可以读取 portfolio"""
        result = auth_service.check_permission(
            test_users["viewer"].id, "portfolio", "read"
        )
        assert result is True
    
    def test_viewer_cannot_write_portfolio(self, auth_service, test_users):
        """测试 viewer 不能写入 portfolio"""
        result = auth_service.check_permission(
            test_users["viewer"].id, "portfolio", "write"
        )
        assert result is False
    
    def test_viewer_cannot_delete_portfolio(self, auth_service, test_users):
        """测试 viewer 不能删除 portfolio"""
        result = auth_service.check_permission(
            test_users["viewer"].id, "portfolio", "delete"
        )
        assert result is False
    
    def test_user_can_read_and_write_portfolio(self, auth_service, test_users):
        """测试 user 可以读写 portfolio"""
        user_id = test_users["user"].id
        assert auth_service.check_permission(user_id, "portfolio", "read") is True
        assert auth_service.check_permission(user_id, "portfolio", "write") is True
    
    def test_user_cannot_delete_portfolio(self, auth_service, test_users):
        """测试 user 不能删除 portfolio"""
        result = auth_service.check_permission(
            test_users["user"].id, "portfolio", "delete"
        )
        assert result is False
    
    def test_user_cannot_access_user_management(self, auth_service, test_users):
        """测试 user 不能访问用户管理"""
        result = auth_service.check_permission(
            test_users["user"].id, "user_management", "read"
        )
        assert result is False
    
    def test_admin_has_full_permissions(self, auth_service, test_users):
        """测试 admin 拥有完整权限"""
        admin_id = test_users["admin"].id
        assert auth_service.check_permission(admin_id, "portfolio", "read") is True
        assert auth_service.check_permission(admin_id, "portfolio", "write") is True
        assert auth_service.check_permission(admin_id, "portfolio", "delete") is True
        assert auth_service.check_permission(admin_id, "user_management", "read") is True
        assert auth_service.check_permission(admin_id, "user_management", "write") is True
    
    def test_locked_user_has_no_permissions(self, auth_service, test_users):
        """测试被锁定的用户没有权限"""
        result = auth_service.check_permission(
            test_users["locked"].id, "portfolio", "read"
        )
        assert result is False
    
    def test_inactive_user_has_no_permissions(self, auth_service, test_users):
        """测试未激活的用户没有权限"""
        result = auth_service.check_permission(
            test_users["inactive"].id, "portfolio", "read"
        )
        assert result is False
    
    def test_nonexistent_user_has_no_permissions(self, auth_service):
        """测试不存在的用户没有权限"""
        result = auth_service.check_permission(
            "nonexistent-id", "portfolio", "read"
        )
        assert result is False
    
    def test_nonexistent_resource_has_no_permissions(self, auth_service, test_users):
        """测试不存在的资源没有权限"""
        result = auth_service.check_permission(
            test_users["admin"].id, "nonexistent_resource", "read"
        )
        assert result is False


class TestGetUserPermissions:
    """测试获取用户权限功能"""
    
    def test_get_viewer_permissions(self, auth_service, test_users):
        """测试获取 viewer 的权限列表"""
        permissions = auth_service.get_user_permissions(test_users["viewer"].id)
        assert len(permissions) > 0
        assert all(isinstance(p, Permission) for p in permissions)
        
        # 验证 viewer 只有读权限
        for perm in permissions:
            assert perm.role == "viewer"
            assert perm.actions == ["read"]
    
    def test_get_user_permissions(self, auth_service, test_users):
        """测试获取 user 的权限列表"""
        permissions = auth_service.get_user_permissions(test_users["user"].id)
        assert len(permissions) > 0
        
        # 验证 user 有读写权限
        portfolio_perm = next((p for p in permissions if p.resource == "portfolio"), None)
        assert portfolio_perm is not None
        assert "read" in portfolio_perm.actions
        assert "write" in portfolio_perm.actions
        assert "delete" not in portfolio_perm.actions
    
    def test_get_admin_permissions(self, auth_service, test_users):
        """测试获取 admin 的权限列表"""
        permissions = auth_service.get_user_permissions(test_users["admin"].id)
        assert len(permissions) > 0
        
        # 验证 admin 有完整权限
        user_mgmt_perm = next((p for p in permissions if p.resource == "user_management"), None)
        assert user_mgmt_perm is not None
        assert "read" in user_mgmt_perm.actions
        assert "write" in user_mgmt_perm.actions
        assert "delete" in user_mgmt_perm.actions
    
    def test_get_permissions_for_nonexistent_user(self, auth_service):
        """测试获取不存在用户的权限"""
        permissions = auth_service.get_user_permissions("nonexistent-id")
        assert permissions == []


class TestRoleAssignment:
    """测试角色分配功能"""
    
    def test_assign_valid_role(self, auth_service, test_users):
        """测试分配有效角色"""
        user_id = test_users["user"].id
        result = auth_service.assign_role(user_id, "admin")
        assert result is True
        
        # 验证角色已更新
        assert auth_service.get_user_role(user_id) == "admin"
    
    def test_assign_invalid_role(self, auth_service, test_users):
        """测试分配无效角色"""
        with pytest.raises(ValueError) as exc_info:
            auth_service.assign_role(test_users["user"].id, "invalid_role")
        assert "Invalid role" in str(exc_info.value)
    
    def test_assign_role_to_nonexistent_user(self, auth_service):
        """测试为不存在的用户分配角色"""
        result = auth_service.assign_role("nonexistent-id", "admin")
        assert result is False
    
    def test_update_role(self, auth_service, test_users):
        """测试更新角色"""
        user_id = test_users["viewer"].id
        result = auth_service.update_role(user_id, "user")
        assert result is True
        assert auth_service.get_user_role(user_id) == "user"
    
    def test_role_change_affects_permissions(self, auth_service, test_users):
        """测试角色变更影响权限"""
        user_id = test_users["viewer"].id
        
        # viewer 不能写入
        assert auth_service.check_permission(user_id, "portfolio", "write") is False
        
        # 升级为 user
        auth_service.assign_role(user_id, "user")
        
        # 现在可以写入
        assert auth_service.check_permission(user_id, "portfolio", "write") is True


class TestRoleQueries:
    """测试角色查询功能"""
    
    def test_get_user_role(self, auth_service, test_users):
        """测试获取用户角色"""
        assert auth_service.get_user_role(test_users["viewer"].id) == "viewer"
        assert auth_service.get_user_role(test_users["user"].id) == "user"
        assert auth_service.get_user_role(test_users["admin"].id) == "admin"
    
    def test_get_role_for_nonexistent_user(self, auth_service):
        """测试获取不存在用户的角色"""
        assert auth_service.get_user_role("nonexistent-id") is None
    
    def test_has_role(self, auth_service, test_users):
        """测试检查用户是否具有指定角色"""
        assert auth_service.has_role(test_users["admin"].id, "admin") is True
        assert auth_service.has_role(test_users["admin"].id, "user") is False
    
    def test_is_admin(self, auth_service, test_users):
        """测试检查是否是管理员"""
        assert auth_service.is_admin(test_users["admin"].id) is True
        assert auth_service.is_admin(test_users["user"].id) is False
        assert auth_service.is_admin(test_users["viewer"].id) is False


class TestResourcePermissions:
    """测试资源权限查询"""
    
    def test_get_resource_permissions(self, auth_service, test_users):
        """测试获取特定资源的权限"""
        viewer_perms = auth_service.get_resource_permissions(
            test_users["viewer"].id, "portfolio"
        )
        assert viewer_perms == ["read"]
        
        user_perms = auth_service.get_resource_permissions(
            test_users["user"].id, "portfolio"
        )
        assert "read" in user_perms
        assert "write" in user_perms
        
        admin_perms = auth_service.get_resource_permissions(
            test_users["admin"].id, "portfolio"
        )
        assert "read" in admin_perms
        assert "write" in admin_perms
        assert "delete" in admin_perms
    
    def test_get_permissions_for_nonexistent_resource(self, auth_service, test_users):
        """测试获取不存在资源的权限"""
        perms = auth_service.get_resource_permissions(
            test_users["admin"].id, "nonexistent_resource"
        )
        assert perms == []


class TestStaticMethods:
    """测试静态方法"""
    
    def test_get_all_resources(self):
        """测试获取所有资源列表"""
        resources = AuthorizationService.get_all_resources()
        assert isinstance(resources, list)
        assert len(resources) > 0
        assert "portfolio" in resources
        assert "market_data" in resources
        assert "user_management" in resources
    
    def test_get_role_permissions_matrix(self):
        """测试获取角色权限矩阵"""
        matrix = AuthorizationService.get_role_permissions_matrix()
        assert isinstance(matrix, dict)
        assert "viewer" in matrix
        assert "user" in matrix
        assert "admin" in matrix
        
        # 验证矩阵结构
        assert isinstance(matrix["viewer"], dict)
        assert isinstance(matrix["viewer"]["portfolio"], list)


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_empty_action(self, auth_service, test_users):
        """测试空操作"""
        result = auth_service.check_permission(
            test_users["admin"].id, "portfolio", ""
        )
        assert result is False
    
    def test_case_sensitive_resource(self, auth_service, test_users):
        """测试资源名称大小写敏感"""
        result = auth_service.check_permission(
            test_users["admin"].id, "Portfolio", "read"
        )
        assert result is False  # 应该区分大小写
    
    def test_case_sensitive_action(self, auth_service, test_users):
        """测试操作名称大小写敏感"""
        result = auth_service.check_permission(
            test_users["admin"].id, "portfolio", "Read"
        )
        assert result is False  # 应该区分大小写
