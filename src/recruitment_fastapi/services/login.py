from recruitment_fastapi.models.user import User
from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.schemas.auth import LoginSchema
from recruitment_fastapi.services.password import password_hash


class LoginService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def authenticate(self, data: LoginSchema) -> User:
        user = await self.repository.find_by_email(data.email)

        if user and self.__verify_password(
            data.password.get_secret_value(), user.password_hash
        ):
            return user
        else:
            return False

    def __verify_password(self, password: str, hashed: str) -> bool:
        return password_hash.verify(password, hashed)
