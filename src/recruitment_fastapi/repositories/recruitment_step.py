from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from recruitment_fastapi.models import RecruitmentStep, Role, User


class RecruitmentStepRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recruitment_step) -> RecruitmentStep:
        self.session.add(recruitment_step)
        await self.session.commit()
        await self.session.refresh(recruitment_step)
        return recruitment_step

    async def create_all(
        self, recruitment_steps: list[RecruitmentStep]
    ) -> list[RecruitmentStep]:
        self.session.add_all(recruitment_steps)
        await self.session.commit()

        return recruitment_steps

    async def find_by_candidate(self, candidate_id: int) -> list[RecruitmentStep]:
        result = await self.session.execute(
            select(RecruitmentStep).where(RecruitmentStep.candidate_id == candidate_id)
        )
        return list(result.scalars().all())

    async def find(self, id: int) -> RecruitmentStep | None:
        load_options = [
            selectinload(RecruitmentStep.candidate),
            selectinload(RecruitmentStep.interviewer),
        ]

        return await self.session.get(RecruitmentStep, id, options=load_options)

    async def allowed_interviewer(self, interviewer_id, roles) -> int | None:
        stmt = (
            select(User.id)
            .join(User.roles)
            .where(Role.key.in_(roles))
            .where(User.id == interviewer_id)
            .limit(1)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def save(self, recruitment_step) -> RecruitmentStep:
        await self.session.commit()
        await self.session.refresh(recruitment_step)

        return recruitment_step

    async def all(self) -> list[RecruitmentStep]:
        stmt = select(RecruitmentStep).options(
            selectinload(RecruitmentStep.candidate),
            selectinload(RecruitmentStep.interviewer),
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def save_all(self, candidate=None):
        await self.session.commit()
        if candidate is not None:
            await self.session.refresh(candidate)
