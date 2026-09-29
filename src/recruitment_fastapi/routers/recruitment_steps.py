from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from recruitment_fastapi.dependencies.auth import CurrentUserDep
from recruitment_fastapi.dependencies.permissions import require_permission
from recruitment_fastapi.dependencies.services import RecruitmentStepServiceDep
from recruitment_fastapi.models import RecruitmentStep
from recruitment_fastapi.schemas.recruitment_steps import (
    AssignInterviewerSchema,
    RecruitmentStepResponseSchema,
    ReviewSchema,
)

router = APIRouter(
    prefix="/recruitment_steps",
    tags=["recruitment_steps"],
    dependencies=[Depends(require_permission("recruitment_steps:access"))],
)

StepIdPath = Annotated[int, Path(ge=1)]


async def get_step(
    id: StepIdPath, step_service: RecruitmentStepServiceDep
) -> RecruitmentStep:
    step = await step_service.find(id)
    if step is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Step not found"
        )

    return step


GetStepDep = Annotated[RecruitmentStep, Depends(get_step)]


async def is_interviewer(
    step: GetStepDep, current_user: CurrentUserDep
) -> RecruitmentStep:
    if step.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    return step


IsInterviewerDep = Annotated[RecruitmentStep, Depends(is_interviewer)]


@router.get(
    "/",
    dependencies=[Depends(require_permission("recruitment_steps:view"))],
)
async def get_recruitment_steps(
    step_service: RecruitmentStepServiceDep,
) -> list[RecruitmentStepResponseSchema]:
    return await step_service.all()


@router.post(
    "/{id}/assign_interviewer",
    dependencies=[Depends(require_permission("recruitment_steps:assign_interviewer"))],
)
async def assign_interviewer(
    id: StepIdPath,
    step: GetStepDep,
    data: AssignInterviewerSchema,
    step_service: RecruitmentStepServiceDep,
) -> RecruitmentStepResponseSchema:
    return await step_service.assign_interviewer(step, data)


@router.post(
    "/{id}/interview_complete",
    dependencies=[Depends(require_permission("recruitment_steps:review"))],
    response_model=RecruitmentStepResponseSchema,
)
async def interview_complete(
    id: StepIdPath, step: IsInterviewerDep, step_service: RecruitmentStepServiceDep
) -> RecruitmentStepResponseSchema:
    return await step_service.interview_complete(step)


@router.post(
    "/{id}/review",
    dependencies=[Depends(require_permission("recruitment_steps:review"))],
    response_model=RecruitmentStepResponseSchema,
)
async def post_review(
    id: StepIdPath,
    step: IsInterviewerDep,
    data: ReviewSchema,
    step_service: RecruitmentStepServiceDep,
) -> RecruitmentStepResponseSchema:
    return await step_service.review(step, data)


@router.post(
    "/{id}/approve",
    dependencies=[Depends(require_permission("recruitment_steps:approve"))],
    response_model=RecruitmentStepResponseSchema,
)
async def approve(
    id: StepIdPath, step: IsInterviewerDep, step_service: RecruitmentStepServiceDep
) -> RecruitmentStepResponseSchema:
    return await step_service.approve(step)


@router.post(
    "/{id}/reject",
    dependencies=[Depends(require_permission("recruitment_steps:reject"))],
    response_model=RecruitmentStepResponseSchema,
)
async def reject(
    id: StepIdPath, step: IsInterviewerDep, step_service: RecruitmentStepServiceDep
) -> RecruitmentStepResponseSchema:
    recruitment_step = await step_service.reject(step)
    return recruitment_step
