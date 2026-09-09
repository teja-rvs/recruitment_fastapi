from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation
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

            if isinstance(exc.orig, UniqueViolation):
                messages = []
                if exc.orig.diag.constraint_name == "ix_candidates_email":
                    messages.append("Email already taken")

                if exc.orig.diag.constraint_name == "ix_candidates_phone":
                    messages.append("Phone already taken")

                raise DuplicateResourceError(
                    ', '.join(messages)
                )

            raise
