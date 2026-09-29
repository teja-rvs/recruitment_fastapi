from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.models.permission import Permission
from recruitment_fastapi.repositories.permission import PermissionRepository
from recruitment_fastapi.schemas.permissions import CreatePermissionSchema
from recruitment_fastapi.services.permission import PermissionService

pytestmark = pytest.mark.unit


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=PermissionRepository)


@pytest.fixture
def service(repository: PermissionRepository) -> PermissionService:
    return PermissionService(repository)


@pytest.fixture
def create_permission():
    return CreatePermissionSchema(model="model", permission="permission")


@pytest.fixture
def permission():
    return Permission(name="model:permission")


@pytest.mark.asyncio
async def test_create_successful(service, repository, create_permission, permission):
    repository.find_by_name.return_value = None
    repository.create.return_value = permission

    result = await service.create(create_permission)

    assert result is permission
    assert result.name == permission.name

    repository.find_by_name.assert_awaited_once_with(permission.name)
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_existing_returns_none(
    service, repository, create_permission, permission
):
    repository.find_by_name.return_value = permission

    result = await service.create(create_permission)

    assert result is None
    repository.find_by_name.assert_awaited_once_with(permission.name)
    repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_permission_for_user_return_true(service, repository):
    repository.check_permission_for_user.return_value = True

    result = await service.check_permission_for_user(1, "model:test")

    assert result is True


@pytest.mark.asyncio
async def test_check_permission_for_user_return_false(service, repository):
    repository.check_permission_for_user.return_value = False

    result = await service.check_permission_for_user(1, "model:test")

    assert result is False


@pytest.fixture
def permissions():
    return [
        Permission(id=1, name="model1:permission"),
        Permission(id=2, name="model2:permission"),
        Permission(id=3, name="model3:permission"),
    ]


@pytest.mark.asyncio
async def test_get_permissions_returns_permissions(service, repository, permissions):
    repository.get_by_ids.return_value = permissions

    result = await service.get_permissions([1, 2, 3])

    assert result is permissions
    repository.get_by_ids.assert_awaited_once_with([1, 2, 3])


@pytest.mark.asyncio
async def test_get_permissions_returns_None(service, repository):
    repository.get_by_ids.return_value = []

    result = await service.get_permissions([1, 2, 3])

    assert result is None
    repository.get_by_ids.assert_awaited_once_with([1, 2, 3])


@pytest.mark.asyncio
async def test_get_permissions_returns_none_for_missing_permission(
    service, repository, permissions
):
    repository.get_by_ids.return_value = permissions[1:]

    result = await service.get_permissions([1, 2, 3])

    assert result is None
    repository.get_by_ids.assert_awaited_once_with([1, 2, 3])


@pytest.mark.asyncio
async def test_all(service, repository, permissions):
    repository.all.return_value = permissions

    result = await service.all()

    assert result is permissions
    repository.all.assert_awaited_once()
