from recruitment_fastapi.models.user import User

from .base import BaseTestFactory


class UserFactory(BaseTestFactory[User]):
    __model__ = User
