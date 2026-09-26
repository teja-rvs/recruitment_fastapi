from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import BackgroundTasks

from recruitment_fastapi.errors.invalid_state_error import InvalidStateError
from recruitment_fastapi.errors.resource_not_found_error import ResourceNotFoundError
from recruitment_fastapi.jobs.run_recruitment_process import run_recruitment_process
from recruitment_fastapi.models import Candidate, RecruitmentStep, User
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository
from recruitment_fastapi.schemas.recruitment_steps import (
    AssignInterviewerSchema,
    ReviewSchema,
)
from recruitment_fastapi.services.recruitment_step import RecruitmentStepService

pytestmark = pytest.mark.unit


@pytest.fixture
def background_tasks() -> Mock:
    return Mock(spec=BackgroundTasks)


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=RecruitmentStepRepository)


@pytest.fixture
def service(
    repository: RecruitmentStepRepository, background_tasks: Mock
) -> RecruitmentStepService:
    return RecruitmentStepService(repository, background_tasks)


@pytest.fixture
def candidate():
    return Candidate(id=1)


@pytest.fixture
def recruitment_steps():
    return [RecruitmentStep(id=1), RecruitmentStep(id=2), RecruitmentStep(id=3)]


@pytest.fixture
def interviewer():
    return User(id=1)


@pytest.mark.asyncio
async def test_all(repository, service, recruitment_steps):
    repository.all.return_value = recruitment_steps

    result = await service.all()

    assert result is recruitment_steps
    repository.all.assert_awaited_once()


@pytest.fixture
def in_progress_step(candidate: Candidate):
    step = RecruitmentStep(id=1, candidate_id=candidate.id, candidate=candidate)
    step.start()
    return step


@pytest.mark.asyncio
async def test_find(repository, service, in_progress_step):
    repository.find.return_value = in_progress_step

    result = await service.find(in_progress_step.id)

    assert result is in_progress_step
    repository.find.assert_awaited_once_with(in_progress_step.id)


@pytest.fixture
def assign_interviewer_data(interviewer):
    interview_date = (datetime.now(tz=UTC).date() + timedelta(days=1)).isoformat()

    return AssignInterviewerSchema(
        interviewer_id=interviewer.id,
        interview_date=interview_date,
    )


@pytest.mark.asyncio
async def test_assign_interview_updates_step(
    repository, service, in_progress_step, interviewer, assign_interviewer_data
):
    repository.allowed_interviewer.return_value = interviewer
    repository.save.return_value = in_progress_step

    result = await service.assign_interviewer(in_progress_step, assign_interviewer_data)

    assert result.status == "interview_scheduled"
    assert result.interviewer_id == interviewer.id
    assert (
        result.interview_date.isoformat()
        == assign_interviewer_data.interview_date.isoformat()
    )
    repository.allowed_interviewer.assert_awaited_once_with(
        interviewer.id, in_progress_step.allowed_roles()
    )
    repository.save.assert_awaited_once_with(in_progress_step)


@pytest.mark.asyncio
async def test_assign_interview_interviewer_not_found(
    repository, service, in_progress_step, assign_interviewer_data
):
    repository.allowed_interviewer.return_value = None

    with pytest.raises(ResourceNotFoundError, match="Interviewer not found"):
        await service.assign_interviewer(in_progress_step, assign_interviewer_data)
        repository.allowed_interviewer.assert_awaited_once_with(
            interviewer.id, in_progress_step.allowed_roles()
        )


@pytest.mark.asyncio
async def test_assign_interviewer_with_interview_date_only(
    repository, service, in_progress_step, assign_interviewer_data
):
    data = assign_interviewer_data.model_copy()
    data.interviewer_id = None

    repository.save.return_value = in_progress_step

    result = await service.assign_interviewer(in_progress_step, data)

    assert result.status == "in_progress"
    assert result.interviewer_id is None
    assert (
        result.interview_date.isoformat()
        == assign_interviewer_data.interview_date.isoformat()
    )
    repository.allowed_interviewer.assert_not_awaited()
    repository.save.assert_awaited_once_with(in_progress_step)


@pytest.mark.asyncio
async def test_assign_interviewer_with_interviewer_only(
    repository, service, in_progress_step, assign_interviewer_data, interviewer
):
    data = assign_interviewer_data.copy()
    data.interview_date = None

    repository.allowed_interviewer.return_value = interviewer
    repository.save.return_value = in_progress_step

    result = await service.assign_interviewer(in_progress_step, data)

    assert result.status == "in_progress"
    assert result.interviewer_id == interviewer.id
    assert result.interview_date is None
    repository.allowed_interviewer.assert_awaited_once_with(
        interviewer.id, in_progress_step.allowed_roles()
    )
    repository.save.assert_awaited_once_with(in_progress_step)


@pytest.fixture
def interview_scheduled_step(in_progress_step):
    in_progress_step.schedule_interview()
    return in_progress_step


@pytest.fixture
def in_review_step(interview_scheduled_step):
    interview_scheduled_step.interview_complete()
    return interview_scheduled_step


@pytest.mark.asyncio
async def test_review(repository, service, in_review_step):
    repository.save.return_value = in_review_step
    data = ReviewSchema(review="Test review")

    result = await service.review(in_review_step, data)
    assert result.feedback == data.review
    repository.save.assert_awaited_once_with(in_review_step)


@pytest.mark.asyncio
async def test_review_with_not_in_review_step(repository, service, in_progress_step):
    data = ReviewSchema(review="Test review")

    with pytest.raises(
        InvalidStateError, match="Recruitment step must be in review stage"
    ):
        await service.review(in_progress_step, data)
        repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_interview_complete(repository, service, interview_scheduled_step):
    repository.save.return_value = interview_scheduled_step

    result = await service.interview_complete(interview_scheduled_step)

    assert result.status == "in_review"
    repository.save.assert_awaited_once_with(interview_scheduled_step)


@pytest.fixture
def review_done_step(in_review_step):
    in_review_step.feedback = "Test Review"
    return in_review_step


@pytest.mark.asyncio
async def test_approve(repository, service, background_tasks, review_done_step):
    repository.save.return_value = review_done_step

    result = await service.approve(review_done_step)

    background_tasks.add_task.assert_called_once_with(
        run_recruitment_process, review_done_step.candidate_id
    )

    assert result is review_done_step
    repository.save.assert_awaited_once_with(review_done_step)


@pytest.mark.asyncio
async def test_approve_without_feedback(
    repository, service, background_tasks, in_review_step
):
    with pytest.raises(InvalidStateError, match="Provide feedback before approval"):
        await service.approve(in_review_step)
        background_tasks.add_task.assert_not_called()
        repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_reject(repository, service, review_done_step, recruitment_steps):
    repository.save.return_value = review_done_step
    repository.find_by_candidate.return_value = recruitment_steps

    result = await service.reject(review_done_step)

    assert result.status == "rejected"
    assert result.candidate.status == "rejected"
    for step in recruitment_steps:
        assert step.status == "cancelled"


@pytest.mark.asyncio
async def test_reject_without_feedback(repository, service, in_review_step):
    with pytest.raises(InvalidStateError, match="Provide feedback before rejection"):
        await service.reject(in_review_step)
        repository.save.assert_not_awaited()
