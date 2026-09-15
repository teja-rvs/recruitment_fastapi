from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.services.sign_up import SignUpService
from recruitment_fastapi.schemas.auth import SignUpSchema
from recruitment_fastapi.models.user import User

from fastapi import HTTPException


@pytest.fixture
def repository() -> UserRepository:
    repository = AsyncMock(spec=UserRepository)
    repository.create = AsyncMock()
    repository.find_by_email = AsyncMock()
    return repository


@pytest.fixture
def service(repository) -> SignUpService:
    return SignUpService(repository)


@pytest.fixture
def sign_up_data() -> SignUpSchema:
    return SignUpSchema(
        email="test@example.com", password="password", password_confirmation="password"
    )


@pytest.fixture
def user_fixture() -> User:
    return User(email="test@example.com", password_hash="password_hash")


@pytest.mark.asyncio
async def test_successful_sign_up(repository, service, sign_up_data, user_fixture):
    repository.find_by_email.return_value = None
    repository.create.return_value = user_fixture

    user = await service.sign_up(sign_up_data)

    assert user.email == sign_up_data.email


@pytest.mark.asyncio
async def test_sign_up_with_existing_user(
    repository, service, user_fixture, sign_up_data
):
    repository.find_by_email.return_value = user_fixture

    with pytest.raises(HTTPException, match="Email already registered"):
        await service.sign_up(sign_up_data)
