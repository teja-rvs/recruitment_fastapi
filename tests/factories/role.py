from recruitment_fastapi.models.role import Role

from .base import BaseTestFactory


class RoleFactory(BaseTestFactory[Role]):
    __model__ = Role
