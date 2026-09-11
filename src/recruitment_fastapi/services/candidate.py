from recruitment_fastapi.models import EntryCandidate, MidCandidate, SeniorCandidate
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.schemas.candidates import CreateCandidateSchema


class CandidateService:
    def __init__(self, repository: CandidateRepository):
        self.repository = repository

    async def create_candidate(self, data: CreateCandidateSchema):
        candidate_class = self.__candidate_class(data.experience)
        candidate = candidate_class(**data.model_dump())
        return await self.repository.create(candidate)

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
