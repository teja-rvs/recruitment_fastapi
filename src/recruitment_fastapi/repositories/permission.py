from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from recruitment_fastapi.models import Permission, Role, User


class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, permission: Permission) -> Permission:
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)

        return permission

    async def find_by_name(self, name: str) -> Permission | None:
        stmt = select(Permission).where(Permission.name == name)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def check_permission_for_user(
        self,
        user_id: int,
        permission_name: str,
    ) -> bool:
        stmt = select(
            exists().where(
                Permission.name == permission_name,
                Permission.roles.any(Role.users.any(User.id == user_id)),
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one()

    async def get_by_ids(self, ids: list[int]) -> list[Permission]:
        result = await self.session.scalars(
            select(Permission).where(Permission.id.in_(ids))
        )

        return result.all()

    async def all(self) -> list[Permission]:
        result = await self.session.scalars(select(Permission))

        return result.all()
