from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class RecruitmentStepRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recruitment_step):
        self.session.add(recruitment_step)
        await self.session.commit()
        await self.session.refresh(recruitment_step)
        return recruitment_step

    async def create_all(self, recruitment_steps: list[RecruitmentStep]):
        self.session.add_all(recruitment_steps)
        await self.session.commit()
        return recruitment_steps

    async def find_by_candidate(self, candidate_id: int):
        result = await self.session.execute(
            select(RecruitmentStep).where(RecruitmentStep.candidate_id == candidate_id)
        )
        return list(result.scalars().all())
