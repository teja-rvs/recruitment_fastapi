from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError

from recruitment_fastapi.dependencies.auth import get_current_user
from recruitment_fastapi.models.user import User

pytestmark = pytest.mark.unit


@pytest.fixture
def token_service():
    service = Mock()
    service.decode = AsyncMock()
    return service


@pytest.fixture
def user_service():
    service = Mock()
    service.find = AsyncMock()
    return service


@pytest.fixture
def credentials():
    return HTTPAuthorizationCredentials(
        scheme="bearer",
        credentials="valid-token",
    )


@pytest.mark.asyncio
async def test_get_current_user_success(
    token_service,
    user_service,
    credentials,
):
    user = User(id=1)

    token_service.decode.return_value = {"user_id": 1}
    user_service.find.return_value = user

    result = await get_current_user(
        credentials,
        token_service,
        user_service,
    )

    assert result is user

    token_service.decode.assert_awaited_once_with("valid-token")
    user_service.find.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_current_user_without_credentials(
    token_service,
    user_service,
):
    with pytest.raises(
        HTTPException,
        match="Could not validate credentials",
    ) as exc_info:
        await get_current_user(
            None,
            token_service,
            user_service,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    token_service.decode.assert_not_awaited()
    user_service.find.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_with_non_bearer_scheme(
    token_service,
    user_service,
):
    credentials = HTTPAuthorizationCredentials(
        scheme="Basic",
        credentials="some-token",
    )

    with pytest.raises(
        HTTPException,
        match="Could not validate credentials",
    ) as exc_info:
        await get_current_user(
            credentials=credentials,
            token_service=token_service,
            user_service=user_service,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    token_service.decode.assert_not_awaited()
    user_service.find.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(
    token_service,
    user_service,
    credentials,
):
    token_service.decode.side_effect = JWTError()

    with pytest.raises(
        HTTPException,
        match="Could not validate credentials",
    ) as exc_info:
        await get_current_user(
            credentials,
            token_service,
            user_service,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    token_service.decode.assert_awaited_once_with("valid-token")
    user_service.find.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_without_user_id(
    token_service,
    user_service,
    credentials,
):
    token_service.decode.return_value = {}

    with pytest.raises(
        HTTPException,
        match="Could not validate credentials",
    ) as exc_info:
        await get_current_user(
            credentials,
            token_service,
            user_service,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    token_service.decode.assert_awaited_once_with("valid-token")
    user_service.find.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_when_user_not_found(
    token_service,
    user_service,
    credentials,
):
    token_service.decode.return_value = {
        "user_id": 123,
    }
    user_service.find.return_value = None

    with pytest.raises(
        HTTPException,
        match="Could not validate credentials",
    ) as exc_info:
        await get_current_user(
            credentials,
            token_service,
            user_service,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    token_service.decode.assert_awaited_once_with("valid-token")
    user_service.find.assert_awaited_once_with(123)
