from unittest.mock import AsyncMock, Mock

import pytest

from recruitment_fastapi.models import Permission
from recruitment_fastapi.repositories.permission import PermissionRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(session):
    return PermissionRepository(session)


@pytest.fixture
def permission():
    return Permission(id=1, name="model:permission")


@pytest.mark.asyncio
async def test_create_successful(session, repository, permission):
    result = await repository.create(permission)

    assert result is permission
    session.add.assert_called_once_with(permission)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(permission)


@pytest.mark.asyncio
async def test_find_by_name_returns_permission(session, repository, permission):
    result = Mock()
    result.scalar_one_or_none.return_value = permission
    session.execute.return_value = result

    found = await repository.find_by_name(permission.name)

    assert found is permission
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_by_name_returns_none(session, repository):
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    found = await repository.find_by_name("invalid")

    assert found is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_permission_for_user_returns_true(session, repository):
    orm = Mock()
    orm.scalar_one.return_value = True
    session.execute.return_value = orm

    result = await repository.check_permission_for_user(1, "model:permission")

    assert result is True
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_permission_for_user_returns_false(session, repository):
    orm = Mock()
    orm.scalar_one.return_value = False
    session.execute.return_value = orm

    result = await repository.check_permission_for_user(1, "model:invalid")

    assert result is False
    session.execute.assert_awaited_once()


@pytest.fixture
def permissions():
    return [
        Permission(id=1, name="model:access"),
        Permission(id=2, name="model:view"),
        Permission(id=3, name="model:create"),
    ]


@pytest.mark.asyncio
async def test_get_by_ids(session, repository, permissions):
    orm = Mock()
    orm.all.return_value = permissions
    session.scalars.return_value = orm

    result = await repository.get_by_ids([1, 2, 3])

    assert result is permissions
    session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_all(session, repository, permissions):
    orm = Mock()
    orm.all.return_value = permissions
    session.scalars.return_value = orm

    result = await repository.all()

    assert result is permissions

    session.scalars.assert_awaited_once()
