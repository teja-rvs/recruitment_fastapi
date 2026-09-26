from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.models import Role, User
from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.services.user import UserService

pytestmark = pytest.mark.unit


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def service(repository: UserRepository) -> UserService:
    return UserService(repository)


@pytest.fixture
def user():
    return User(id=1, roles=[])


@pytest.mark.asyncio
async def test_find_returns_user(repository, service, user):
    repository.find.return_value = user

    result = await service.find(user.id)

    assert result is user
    repository.find.assert_awaited_once_with(user.id)


@pytest.mark.asyncio
async def test_find_returns_none(repository, service):
    repository.find.return_value = None

    result = await service.find(1)

    assert result is None
    repository.find.assert_awaited_once_with(1)


@pytest.fixture
def roles():
    return [Role(id=1), Role(id=2), Role(id=3)]


@pytest.mark.asyncio
async def test_assign_roles(repository, service, user, roles):
    repository.save.return_value = user

    result = await service.assign_roles(user, roles)

    assert result is user
    assert result.roles == roles


@pytest.mark.asyncio
async def test_assign_roles_does_not_create_duplicate(repository, service, roles):
    user = User(id=1, roles=[roles[0]])
    repository.save.return_value = user

    result = await service.assign_roles(user, roles)

    assert result is user
    assert result.roles == roles


@pytest.fixture()
def users():
    return [User(id=1), User(id=2), User(id=3)]


@pytest.mark.asyncio
async def test_all(repository, service, users):
    repository.all.return_value = users

    result = await service.all()

    assert result is users
    repository.all.assert_awaited_once()
