from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.models.user import User
from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.schemas.auth import LoginSchema
from recruitment_fastapi.services.login import LoginService
from recruitment_fastapi.services.password import password_hash


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def service(repository: AsyncMock) -> LoginService:
    return LoginService(repository)


@pytest.fixture
def db_user() -> User:
    return User(
        email="test@example.com",
        password_hash=password_hash.hash("password"),
    )


@pytest.fixture
def login_data() -> LoginSchema:
    return LoginSchema(
        email="test@example.com",
        password="password",
    )


@pytest.mark.asyncio
async def test_authenticate_returns_user_for_valid_credentials(
    repository,
    service,
    db_user,
    login_data,
):
    repository.find_by_email.return_value = db_user

    user = await service.authenticate(login_data)

    assert user == db_user
    repository.find_by_email.assert_awaited_once_with(login_data.email)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("invalid@example.com", "password"),
        ("test@example.com", "invalid-password"),
    ],
)
async def test_authenticate_returns_false_for_invalid_credentials(
    repository,
    service,
    email,
    password,
):
    repository.find_by_email.return_value = None

    login_data = LoginSchema(
        email=email,
        password=password,
    )

    user = await service.authenticate(login_data)

    assert user is False
