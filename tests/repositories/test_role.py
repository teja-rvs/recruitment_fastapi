from unittest.mock import AsyncMock, Mock

import pytest

from recruitment_fastapi.models.role import Role
from recruitment_fastapi.repositories.role import RoleRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(session: AsyncMock) -> RoleRepository:
    return RoleRepository(session)


@pytest.fixture
def role():
    return Role(name="Test Role", key="test_role")


@pytest.mark.asyncio
async def test_find_by_key_returns_role(session, repository, role):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = role
    session.execute.return_value = execute_result

    result = await repository.find_by_key(role.key)

    assert result is role
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_by_key_returns_None(session, repository):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = None
    session.execute.return_value = execute_result

    result = await repository.find_by_key("invalid_key")

    assert result is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create(session, repository, role):
    result = await repository.create(role)

    assert result is role
    session.add.assert_called_once_with(role)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(role)


@pytest.fixture
def roles():
    return [
        Role(name="Role One", key="role_one"),
        Role(name="Role Two", key="role_two"),
        Role(name="Role Three", key="role_three"),
    ]


@pytest.mark.asyncio
async def test_get_by_ids(session, repository, roles):
    scalars_mock = Mock()
    scalars_mock.all.return_value = roles
    session.scalars.return_value = scalars_mock

    result = await repository.get_by_ids([1, 2, 3])

    assert result is roles
    session.scalars.assert_awaited_once()
    scalars_mock.all.assert_called_once()


@pytest.mark.asyncio
async def test_all(session, repository, roles):
    scalars_mock = Mock()
    execute_mock = Mock()

    scalars_mock.all.return_value = roles
    execute_mock.scalars.return_value = scalars_mock
    session.execute.return_value = execute_mock

    result = await repository.all()

    assert result is roles


@pytest.mark.asyncio
async def test_find_return_role(session, repository, role):
    session.get.return_value = role

    result = await repository.find(role.id)

    assert result is role
    session.get.assert_awaited_once_with(Role, role.id)


@pytest.mark.asyncio
async def test_find_return_none(session, repository):
    session.get.return_value = None

    result = await repository.find(1)

    assert result is None
    session.get.assert_awaited_once_with(Role, 1)


@pytest.mark.asyncio
async def test_find_with_permissions_returns_role(session, repository, role):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = role
    session.execute.return_value = execute_result

    result = await repository.find_with_permissions(role.id)

    assert result is role
    session.execute.assert_awaited_once()
    execute_result.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_find_with_permissions_returns_none(session, repository):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = None
    session.execute.return_value = execute_result

    result = await repository.find_with_permissions(1)

    assert result is None
    session.execute.assert_awaited_once()
    execute_result.scalar_one_or_none.assert_called_once()
