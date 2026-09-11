from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from recruitment_fastapi.database import SessionDep
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


def get_candidate_service(session: SessionDep) -> CandidateService:
    return CandidateService(CandidateRepository(session))


CandidateServiceDep = Annotated[CandidateService, Depends(get_candidate_service)]


@router.post("/register")
async def register_candidate(
    candidate: CreateCandidateSchema,
    service: CandidateServiceDep,
) -> CandidateResponseSchema:
    try:
        created = await service.create_candidate(candidate)
    except DuplicateResourceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return CandidateResponseSchema.model_validate(created)
