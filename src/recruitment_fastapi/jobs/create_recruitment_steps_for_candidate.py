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
        for step_class in candidate.RECRUITMENT_STEPS
    ]

    recruitment_steps = await recruitment_step_repository.create_all(steps)

    phone_screener_steps = [
        step for step in recruitment_steps if step.type == "phone_screener_step"
    ]

    for step in phone_screener_steps:
        step.start()
        await recruitment_step_repository.save(step)

    return True


async def run_create_recruitment_steps_for_candidate(candidate_id: int):
    async with AsyncSessionLocal() as session:
        return await create_recruitment_steps_for_candidate(
            candidate_id,
            CandidateRepository(session),
            RecruitmentStepRepository(session),
        )
