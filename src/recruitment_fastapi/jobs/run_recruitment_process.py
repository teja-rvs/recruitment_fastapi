from recruitment_fastapi.database import AsyncSessionLocal
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.services.recruitment_process import RecruitmentProcessService


async def run_recruitment_process(candidate_id: int):
    async with AsyncSessionLocal() as session:
        return await RecruitmentProcessService(
            candidate_id, CandidateRepository(session)
        ).run()
