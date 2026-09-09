from recruitment_fastapi.models import EntryCandidate, MidCandidate, SeniorCandidate
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.schemas.candidates import CreateCandidateSchema


class CandidateService:
    def __init__(self, respository: CandidateRepository):
        self.respository = respository

    def candidate_klass(self, exp: int):
        if exp <= 3:
            return EntryCandidate
        elif exp <= 6:
            return MidCandidate
        else:
            return SeniorCandidate

    async def create_candidate(self, data: CreateCandidateSchema):
        candidate = self.candidate_klass(data.experience)(**data.model_dump())
        return await self.respository.create(candidate)
