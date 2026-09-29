from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from recruitment_fastapi.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_email(self, email) -> User | None:
        users = await self.session.execute(select(User).filter_by(email=email))
        return users.scalar_one_or_none()

    async def create(self, user) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def find(self, id) -> User | None:
        user = await self.session.get(User, id)
        return user

    async def find_with_roles(self, id) -> User | None:
        stmt = select(User).options(selectinload(User.roles)).where(User.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, user) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        relationship_names = [
            relationship.key for relationship in inspect(user).mapper.relationships
        ]
        if relationship_names:
            await self.session.refresh(user, attribute_names=relationship_names)
        return user

    async def all(self) -> list[User]:
        roles = await self.session.execute(select(User))
        return roles.scalars().all()
