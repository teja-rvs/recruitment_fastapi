from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from recruitment_fastapi.database import get_session
from recruitment_fastapi.errors.duplicate_resource_error import DuplicateResourceError
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.schemas.candidates import (
    CandidateResponseSchema,
    CreateCandidateSchema,
)
from recruitment_fastapi.services.candidate import CandidateService

router = APIRouter(
    prefix="/candidates",
    tags=["candidates"],
)


def get_candidate_service(
    session: AsyncSession = Depends(get_session),
) -> CandidateService:

    repository = CandidateRepository(session)

    return CandidateService(repository)


@router.post(
    "/register",
    response_model=CandidateResponseSchema,
)
async def register_candidate(
    candidate: CreateCandidateSchema,
    service: CandidateService = Depends(get_candidate_service),
):
    try:
        candidate = await service.create_candidate(candidate)
        return candidate

    except DuplicateResourceError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
