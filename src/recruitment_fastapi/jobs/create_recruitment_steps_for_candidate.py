from recruitment_fastapi.database import AsyncSessionLocal
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository


async def create_recruitment_steps_for_candidate(candidate_id: int):
    async with AsyncSessionLocal() as session:
        candidate_repository = CandidateRepository(session)
        recruitment_step_repository = RecruitmentStepRepository(session)

        candidate = await candidate_repository.find(candidate_id)
        steps = type(candidate).RECRUITMENT_STEPS
        for step_class in steps:
            step = step_class(candidate_id=candidate.id)
            await recruitment_step_repository.create_all(step)

        await session.commit()
