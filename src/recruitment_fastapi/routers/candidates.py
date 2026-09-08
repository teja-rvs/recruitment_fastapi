from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from recruitment_fastapi.database import get_db
from recruitment_fastapi.models.candidate import Candidate
from recruitment_fastapi.respositories.candidate import CandidateRepository
from recruitment_fastapi.schemas.candidates import (
    CreateCandidateSchema,
    CandidateResponseSchema,
)
from recruitment_fastapi.services.candidate import CandidateService
from recruitment_fastapi.errors.duplicate_resource_error import DuplicateResourceError


router = APIRouter(
    prefix="/candidates",
    tags=["candidates"],
)


def get_candidate_service(
    session: AsyncSession = Depends(get_db),
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
        return await service.create_candidate(candidate)
    except DuplicateResourceError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )