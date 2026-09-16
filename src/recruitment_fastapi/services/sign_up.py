from asyncer import asyncify

from recruitment_fastapi.models.user import User
from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.schemas.auth import SignUpSchema
from recruitment_fastapi.services.password import password_hash


class SignUpService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def sign_up(self, data: SignUpSchema) -> User:
        user = await self.repository.find_by_email(data.email)

        if user:
            return False

        hashed_password = await asyncify(password_hash.hash)(
            data.password.get_secret_value()
        )
        user = User(
            email=data.email,
            password_hash=hashed_password,
        )

        return await self.repository.create(user)
