from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from recruitment_fastapi.services.token import ALGORITHM, TokenService

pytestmark = pytest.mark.unit

TOKEN_SECRET = "unit-test-token-secret"


@pytest.fixture
def token_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setattr(
        "recruitment_fastapi.services.token.SECRET_KEY",
        TOKEN_SECRET,
    )
    return TOKEN_SECRET


@pytest.fixture
def token_service(token_secret: str) -> TokenService:
    return TokenService()


@pytest.mark.asyncio
async def test_encode(token_service: TokenService, token_secret: str):
    result = await token_service.encode({"key": "value"})

    decoded = jwt.decode(result, token_secret, algorithms=[ALGORITHM])
    assert decoded["key"] == "value"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_encode_with_expiry_delta(token_service: TokenService, token_secret: str):
    before = datetime.now(UTC)
    result = await token_service.encode({"key": "value"}, timedelta(hours=1))

    decoded = jwt.decode(result, token_secret, algorithms=[ALGORITHM])
    assert decoded["key"] == "value"
    assert decoded["exp"] == pytest.approx(
        (before + timedelta(hours=1)).timestamp(), abs=1
    )
