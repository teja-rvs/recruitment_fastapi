from datetime import UTC, datetime, timedelta

from asyncer import asyncify
from jose import jwt

from recruitment_fastapi.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"


class TokenService:
    async def encode(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()

        if expires_delta is not None:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(hours=6)

        to_encode.update({"exp": expire})

        return await asyncify(jwt.encode)(to_encode, SECRET_KEY, ALGORITHM)
