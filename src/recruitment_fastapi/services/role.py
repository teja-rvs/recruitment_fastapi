from recruitment_fastapi.models.role import Role
from recruitment_fastapi.repositories.role import RoleRepository
from recruitment_fastapi.schemas.roles import CreateRoleSchema


class RoleService:
    def __init__(self, repository: RoleRepository):
        self.repository = repository

    async def create(self, data: CreateRoleSchema):
        key = self._generate_key(data.name)
        existing_role = await self.repository.find_by_key(key)

        if existing_role:
            return None

        role = Role(name=data.name, key=key)
        return await self.repository.create(role)

    async def get_roles(self, ids):
        ids = list(set(ids))
        roles = await self.repository.get_by_ids(ids)

        if not roles:
            return None

        if len(roles) != len(ids):
            return None

        return roles

    async def all(self):
        return await self.repository.all()

    async def find_with_permissions(self, id):
        role = await self.repository.find_with_permissions(id)

        return role

    async def assign_permissions(self, role, permissions):
        for permission in permissions:
            if permission not in role.permissions:
                role.permissions.append(permission)

        return await self.repository.save(role)

    def _generate_key(self, name: str) -> str:
        return name.lower().replace(" ", "_")
