from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from recruitment_fastapi.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_email(self, email):
        users = await self.session.execute(select(User).filter_by(email=email))
        return users.scalar_one_or_none()

    async def create(self, user) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
