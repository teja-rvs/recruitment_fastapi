from typing import Annotated

from fastapi import BackgroundTasks, Depends

from recruitment_fastapi.database import SessionDep
from recruitment_fastapi.jobs.create_recruitment_steps_for_candidate import (
    create_recruitment_steps_for_candidate,
)
from recruitment_fastapi.models import EntryCandidate, MidCandidate, SeniorCandidate
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository
from recruitment_fastapi.schemas.candidates import CreateCandidateSchema


def get_recruitment_step_repository(session: SessionDep) -> RecruitmentStepRepository:
    return RecruitmentStepRepository(session)


RecruitmentStepRepositoryDep = Annotated[
    RecruitmentStepRepository, Depends(get_recruitment_step_repository)
]


class CandidateService:
    def __init__(
        self, repository: CandidateRepository, background_tasks: BackgroundTasks
    ):
        self.repository = repository
        self.background_tasks = background_tasks

    async def create_candidate(self, data: CreateCandidateSchema):
        candidate_class = self.__candidate_class(data.experience)
        candidate = candidate_class(**data.model_dump())
        created_candidate = await self.repository.create(candidate)
        self.background_tasks.add_task(
            create_recruitment_steps_for_candidate, created_candidate.id
        )
        return created_candidate

    # Private

    def __candidate_class(
        self,
        exp: int,
    ) -> type[EntryCandidate | MidCandidate | SeniorCandidate]:
        if exp <= 3:
            return EntryCandidate
        elif exp <= 6:
            return MidCandidate
        else:
            return SeniorCandidate
