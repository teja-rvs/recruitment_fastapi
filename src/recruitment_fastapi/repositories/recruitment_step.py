from sqlalchemy.ext.asyncio import AsyncSession


class RecruitmentStepRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recruitment_step):
        self.session.add(recruitment_step)
        await self.session.commit()
        await self.session.refresh(recruitment_step)
        return recruitment_step

    async def create_all(self, recruitment_step):
        self.session.add(recruitment_step)
        return recruitment_step
