from recruitment_fastapi.models.permission import Permission
from recruitment_fastapi.repositories.permission import PermissionRepository
from recruitment_fastapi.schemas.permissions import CreatePermissionSchema


class PermissionService:
    def __init__(self, repository: PermissionRepository):
        self.repository = repository

    async def create(self, data: CreatePermissionSchema):
        name = self._generate_name(data.model, data.permission)
        existing_permission = await self.repository.find_by_name(name)

        if existing_permission is not None:
            return None

        permission = await self.repository.create(Permission(name=name))
        return permission

    async def check_permission_for_user(self, user_id: int, permission_name: str):
        return await self.repository.check_permission_for_user(user_id, permission_name)

    async def get_permissions(self, ids: list[int]):
        ids = list(set(ids))
        permissions = await self.repository.get_by_ids(ids)

        if not permissions:
            return None

        if len(permissions) != len(ids):
            return None

        return permissions

    async def all(self):
        return await self.repository.all()

    def _generate_name(self, model, permission):
        return f"{model}:{permission}"
