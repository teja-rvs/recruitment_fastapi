from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from recruitment_fastapi.errors.duplicate_resource_error import DuplicateResourceError

class CandidateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, candidate):
        try:
            self.session.add(candidate)
            await self.session.commit()
            await self.session.refresh(candidate)
            return candidate

        except IntegrityError as exc:
            await self.session.rollback()

            if "UniqueViolation" in str(exc.orig):
                raise DuplicateResourceError(
                    "Candidate already exists"
                )
            
            raise