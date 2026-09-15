from fastapi import HTTPException

from recruitment_fastapi.models.user import User
from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.schemas.auth import SignUpSchema
from recruitment_fastapi.services.password import password_hash


class SignUpService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def sign_up(self, data: SignUpSchema) -> User:
        await self.__user_exists(data.email)

        user = User(
            email=data.email,
            password_hash=password_hash.hash(data.password.get_secret_value()),
        )

        return await self.repository.create(user)

    async def __user_exists(self, email: str):
        user = await self.repository.find_by_email(email)

        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
