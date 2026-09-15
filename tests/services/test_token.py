from datetime import UTC, datetime, timedelta

from jose import jwt

from recruitment_fastapi.services.token import ALGORITHM, SECRET_KEY, TokenService


def test_encode():
    service = TokenService()
    result = service.encode({"key": "value"})

    decoded = jwt.decode(result, SECRET_KEY, ALGORITHM)
    assert decoded["key"] == "value"
    assert "exp" in decoded


def test_encode_with_expiry_delta():
    service = TokenService()
    before = datetime.now(UTC)
    result = service.encode({"key": "value"}, timedelta(hours=1))

    decoded = jwt.decode(result, SECRET_KEY, ALGORITHM)
    assert decoded["key"] == "value"
    expiration = datetime.fromtimestamp(decoded["exp"], tz=UTC)

    assert expiration.replace(microsecond=0) == (before + timedelta(hours=1)).replace(
        microsecond=0
    )

    assert "exp" in decoded
