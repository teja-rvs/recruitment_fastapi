from fastapi import APIRouter

from recruitment_fastapi.dependencies.services import CandidateServiceDep
from recruitment_fastapi.schemas.candidates import (
    CandidateResponseSchema,
    CreateCandidateSchema,
)

router = APIRouter(
    prefix="/candidates",
    tags=["candidates"],
)


@router.post("/register")
async def register_candidate(
    candidate: CreateCandidateSchema,
    service: CandidateServiceDep,
) -> CandidateResponseSchema:
    return await service.create_candidate(candidate)
