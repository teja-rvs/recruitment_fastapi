from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from recruitment_fastapi.errors.duplicate_resource_error import DuplicateResourceError
from recruitment_fastapi.models import Candidate, RecruitmentStep
from recruitment_fastapi.states.candidate_status import CandidateStatusMachine
from recruitment_fastapi.states.recruitment_step_status import (
    RecruitmentStepStatusMachine,
)


class CandidateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, candidate) -> Candidate:
        try:
            self.session.add(candidate)
            await self.session.commit()
            await self.session.refresh(candidate)
            return candidate

        except IntegrityError as exc:
            await self.session.rollback()

            if isinstance(exc.orig, UniqueViolation):
                messages = []
                if exc.orig.diag.constraint_name == "ix_candidates_email":
                    messages.append("Email already taken")

                if exc.orig.diag.constraint_name == "ix_candidates_phone":
                    messages.append("Phone already taken")

                raise DuplicateResourceError(", ".join(messages))

            raise

    async def find(self, id: int) -> Candidate | None:
        return await self.session.get(Candidate, id)

    async def find_with_current_recruitment_steps(self, id: int) -> Candidate | None:
        stmt = (
            select(Candidate)
            .options(
                selectinload(
                    Candidate.recruitment_steps.and_(
                        RecruitmentStep.status
                        != RecruitmentStepStatusMachine.cancelled.value
                    )
                )
            )
            .where(
                Candidate.id == id,
                Candidate.status == CandidateStatusMachine.in_progress.value,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, candidate) -> Candidate:
        await self.session.commit()
        await self.session.refresh(candidate)

        return candidate
