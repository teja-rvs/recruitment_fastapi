from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException, status

from recruitment_fastapi.dependencies.permissions import require_permission
from recruitment_fastapi.models.user import User

pytestmark = pytest.mark.unit


@pytest.fixture
def permission_service():
    service = Mock()
    service.check_permission_for_user = AsyncMock()
    return service


@pytest.fixture
def current_user():
    return User(id=1)


@pytest.mark.asyncio
async def test_require_permission_success(current_user, permission_service):
    permission_service.check_permission_for_user.return_value = True

    permission_checker = require_permission("model:permission")

    result = await permission_checker(current_user, permission_service)

    assert result is True
    permission_service.check_permission_for_user.assert_awaited_once_with(
        current_user.id, "model:permission"
    )


@pytest.mark.asyncio
async def test_require_permission_failure(current_user, permission_service):
    permission_service.check_permission_for_user.return_value = False

    permission_checker = require_permission("model:permission")

    with pytest.raises(HTTPException, match="Permission denied") as exc_info:
        await permission_checker(current_user, permission_service)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    permission_service.check_permission_for_user.assert_awaited_once_with(
        current_user.id, "model:permission"
    )
