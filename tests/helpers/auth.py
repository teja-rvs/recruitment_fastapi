import pytest

from recruitment_fastapi.services.token import TokenService


@pytest.fixture
def auth_headers():
    async def create_headers(user):
        token_service = TokenService()
        token = await token_service.encode({"user_id": user.id})

        return {"Authorization": f"Bearer {token}"}

    return create_headers
