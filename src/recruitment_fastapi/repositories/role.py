from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from recruitment_fastapi.models.role import Role


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_key(self, key) -> Role | None:
        stmt = select(Role).where(Role.key == key)
        role = await self.session.execute(stmt)
        return role.scalar_one_or_none()

    async def create(self, role) -> Role:
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def get_by_ids(self, ids) -> list[Role]:
        result = await self.session.scalars(select(Role).where(Role.id.in_(ids)))

        return result.all()

    async def all(self) -> list[Role]:
        roles = await self.session.execute(select(Role))
        return roles.scalars().all()

    async def find(self, id) -> Role | None:
        role = await self.session.get(Role, id)
        return role

    async def save(self, role) -> Role:
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def find_with_permissions(self, id) -> Role | None:
        stmt = select(Role).options(selectinload(Role.permissions)).where(Role.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
