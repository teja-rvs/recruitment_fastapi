from recruitment_fastapi.models.permission import Permission

from .base import BaseTestFactory


class PermissionFactory(BaseTestFactory[Permission]):
    __model__ = Permission
