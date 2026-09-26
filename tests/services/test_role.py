from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.models import Permission, Role
from recruitment_fastapi.repositories.role import RoleRepository
from recruitment_fastapi.schemas.roles import CreateRoleSchema
from recruitment_fastapi.services.role import RoleService

pytestmark = pytest.mark.unit


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=RoleRepository)


@pytest.fixture
def service(repository: RoleRepository) -> AsyncMock:
    return RoleService(repository)


@pytest.fixture
def create_role_data():
    return CreateRoleSchema(name="Test Role")


@pytest.fixture
def role():
    return Role(name="Test Role", key="test_role", permissions=[])


@pytest.mark.asyncio
async def test_create(repository, service, create_role_data, role):
    repository.find_by_key.return_value = None
    repository.create.return_value = role

    result = await service.create(create_role_data)

    assert result.name == role.name
    assert result.key == role.key


@pytest.mark.asyncio
async def test_create_with_existing_role(repository, service, create_role_data, role):
    repository.find_by_key.return_value = role

    result = await service.create(create_role_data)

    assert result is None


@pytest.fixture
def roles():
    return [
        Role(id="1", name="Role One", key="role_one"),
        Role(id="2", name="Role Two", key="role_two"),
        Role(id="3", name="Role Three", key="role_three"),
    ]


@pytest.mark.asyncio
async def test_get_roles(repository, service, roles):
    repository.get_by_ids.return_value = roles

    result = await service.get_roles([1, 2, 3])

    assert result is roles
    repository.get_by_ids.assert_awaited_once_with([1, 2, 3])


@pytest.mark.asyncio
async def test_get_roles_with_no_matching_roles(repository, service):
    repository.get_by_ids.return_value = None

    result = await service.get_roles([1, 2, 3])

    assert result is None
    repository.get_by_ids.assert_awaited_once_with([1, 2, 3])


@pytest.mark.asyncio
async def test_get_roles_with_some_missing_roles(repository, service, roles):
    roles = roles.copy()[1:]
    repository.get_by_ids.return_value = roles

    result = await service.get_roles([1, 2, 3])

    assert result is None
    repository.get_by_ids.assert_awaited_once_with([1, 2, 3])


@pytest.mark.asyncio
async def test_all(repository, service, roles):
    repository.all.return_value = roles

    result = await service.all()

    assert result is roles
    repository.all.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_with_permissions(repository, service, role):
    repository.find_with_permissions.return_value = role

    result = await service.find_with_permissions(role.id)

    assert result is role
    repository.find_with_permissions.assert_awaited_once_with(role.id)


@pytest.mark.asyncio
async def test_find_with_permissions_return_none(repository, service):
    repository.find_with_permissions.return_value = None

    result = await service.find_with_permissions(1)

    assert result is None
    repository.find_with_permissions.assert_awaited_once_with(1)


@pytest.fixture
def permissions():
    return [
        Permission(id=1, name="model:access"),
        Permission(id=2, name="model:create"),
        Permission(id=3, name="model:read"),
        Permission(id=4, name="model:update"),
        Permission(id=5, name="model:delete"),
    ]


@pytest.mark.asyncio
async def test_assign_permissions(repository, service, role, permissions):
    repository.save.return_value = role

    result = await service.assign_permissions(role, permissions)

    assert result is role
    assert result.permissions == permissions


@pytest.mark.asyncio
async def test_assign_permissions_does_not_create_duplicate(
    repository, service, permissions
):
    role = Role(name="Test Role", key="test_role", permissions=[permissions[0]])

    repository.save.return_value = role

    result = await service.assign_permissions(role, permissions)

    assert result is role
    assert result.permissions == permissions
