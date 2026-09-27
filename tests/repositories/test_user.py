from unittest.mock import AsyncMock, Mock, call

import pytest

from recruitment_fastapi.models.user import User
from recruitment_fastapi.repositories.user import UserRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def repository(session: AsyncMock) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
def user() -> User:
    return User(email="test@example.com")


def _scalar_result(value):
    result = Mock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.asyncio
async def test_create(session, repository, user):
    result = await repository.create(user)

    assert result is user
    session.add.assert_called_once_with(user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


@pytest.mark.parametrize(
    ("email", "found"),
    [
        pytest.param("test@example.com", True, id="existing-user"),
        pytest.param("random@example.com", False, id="missing-user"),
    ],
)
@pytest.mark.asyncio
async def test_find_by_email(session, repository, user, email, found):
    expected = user if found else None
    session.execute.return_value = _scalar_result(expected)

    result = await repository.find_by_email(email)

    assert result is expected
    session.execute.assert_awaited_once()


@pytest.mark.parametrize(
    "found",
    [
        pytest.param(True, id="existing-user"),
        pytest.param(False, id="missing-user"),
    ],
)
@pytest.mark.asyncio
async def test_find(session, repository, user, found):
    expected = user if found else None
    user_id = user.id if found else 1
    session.get.return_value = expected

    result = await repository.find(user_id)

    assert result is expected
    session.get.assert_awaited_once_with(User, user_id)


@pytest.mark.parametrize(
    "found",
    [
        pytest.param(True, id="existing-user"),
        pytest.param(False, id="missing-user"),
    ],
)
@pytest.mark.asyncio
async def test_find_with_roles(session, repository, user, found):
    expected = user if found else None
    user_id = user.id if found else 1
    execute_result = _scalar_result(expected)
    session.execute.return_value = execute_result

    result = await repository.find_with_roles(user_id)

    assert result is expected
    session.execute.assert_awaited_once()
    execute_result.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_save(session, repository, user):
    result = await repository.save(user)

    assert result is user
    session.commit.assert_awaited_once()
    session.refresh.assert_has_awaits(
        [
            call(user),
            call(user, attribute_names=["roles"]),
        ]
    )


@pytest.mark.asyncio
async def test_all(session, repository):
    users = [User(id=1), User(id=2)]
    execute_result = Mock()
    execute_result.scalars.return_value.all.return_value = users
    session.execute.return_value = execute_result

    result = await repository.all()

    assert result is users
    session.execute.assert_awaited_once()
    execute_result.scalars.assert_called_once_with()
    execute_result.scalars.return_value.all.assert_called_once_with()
