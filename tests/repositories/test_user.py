from unittest.mock import AsyncMock, Mock

import pytest

from recruitment_fastapi.models.user import User
from recruitment_fastapi.repositories.user import UserRepository


@pytest.fixture
def session() -> AsyncMock:
    mock_session = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.execute = AsyncMock()
    return mock_session


@pytest.fixture
def repository(session) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
def user() -> User:
    return User(email="test@example.com")


@pytest.mark.asyncio
async def test_create(session, repository, user):
    await repository.create(user)

    session.add.assert_called_once_with(user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_find_by_email(session, repository, user):
    await repository.find_by_email(user.email)

    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_email_with_existing_user(session, repository, user):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = user
    session.execute.return_value = execute_result

    result = await repository.find_by_email(user.email)

    session.execute.assert_awaited_once()
    assert result.email == user.email


@pytest.mark.asyncio
async def test_find_by_email_with_no_existing_user(session, repository, user):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = None
    session.execute.return_value = execute_result

    result = await repository.find_by_email("random@example.com")

    session.execute.assert_awaited_once()
    assert result is None
