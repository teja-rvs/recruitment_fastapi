from recruitment_fastapi.database import AsyncSessionLocal
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository


async def create_recruitment_steps_for_candidate(
    candidate_id: int,
    candidate_repository: CandidateRepository,
    recruitment_step_repository: RecruitmentStepRepository,
):
    candidate = await candidate_repository.find(candidate_id)
    steps = [
        step_class(candidate_id=candidate.id)
        for step_class in type(candidate).RECRUITMENT_STEPS
    ]
    await recruitment_step_repository.create_all(steps)

    return True


async def run_create_recruitment_steps_for_candidate(candidate_id: int):
    async with AsyncSessionLocal() as session:
        return await create_recruitment_steps_for_candidate(
            candidate_id,
            CandidateRepository(session),
            RecruitmentStepRepository(session),
        )
