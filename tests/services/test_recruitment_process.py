from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.models import (
    Candidate,
    DsAlgoInterviewStep,
    PhoneScreenerStep,
    RecruitmentStep,
    User,
)
from recruitment_fastapi.models.recruitment_stage import RecruitmentStage
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.services.recruitment_process import RecruitmentProcessService

pytestmark = pytest.mark.unit


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=CandidateRepository)


@pytest.fixture
def service_factory(repository):
    def create_service(candidate) -> RecruitmentProcessService:
        return RecruitmentProcessService(
            candidate_id=candidate.id, candidate_repository=repository
        )

    return create_service


@pytest.fixture
def candidate_factory():
    def create_candidate(recruitment_steps=None) -> Candidate:
        if recruitment_steps is None:
            recruitment_steps = []
        return Candidate(id=1, recruitment_steps=recruitment_steps)

    return create_candidate


@pytest.fixture
def interviewer():
    return User(id=1)


@pytest.fixture
def approved_step_factory(interviewer):
    def create_approved_step(id=1):
        step = RecruitmentStep(id=id)
        step.start()
        step.interviewer = interviewer
        step.interviewer_id = interviewer.id
        step.schedule_interview()
        step.interview_complete()
        step.feedback = "Test Review"
        step.approve()

        return step

    return create_approved_step


@pytest.fixture
def approved_steps(approved_step_factory):
    return [
        approved_step_factory(1),
        approved_step_factory(2),
        approved_step_factory(3),
    ]


@pytest.fixture
def candidate_with_approved_steps(candidate_factory, approved_steps):
    return candidate_factory(approved_steps)


@pytest.fixture
def stages():
    return (
        RecruitmentStage((RecruitmentStep,)),
        RecruitmentStage((PhoneScreenerStep,)),
        RecruitmentStage((DsAlgoInterviewStep,)),
    )


@pytest.fixture
def in_progress_steps(approved_step_factory):
    return [
        approved_step_factory(1),
        PhoneScreenerStep(id=2),
        DsAlgoInterviewStep(id=3),
    ]


@pytest.mark.asyncio
async def test_run_with_invalid_candidate(
    repository, service_factory, candidate_factory
):
    candidate = candidate_factory()
    repository.find_with_current_recruitment_steps.return_value = None
    service = service_factory(candidate)

    result = await service.run()

    assert result is None
    repository.find_with_current_recruitment_steps.assert_awaited_once_with(
        candidate.id
    )


@pytest.mark.asyncio
async def test_run_with_candidate_all_steps_approved(
    repository, service_factory, candidate_with_approved_steps
):
    repository.find_with_current_recruitment_steps.return_value = (
        candidate_with_approved_steps
    )
    repository.save.return_value = candidate_with_approved_steps

    service = service_factory(candidate_with_approved_steps)

    await service.run()

    assert candidate_with_approved_steps.status == "recruited"


@pytest.mark.asyncio
async def test_run_starts_next_stage(
    repository,
    service_factory,
    candidate_factory,
    in_progress_steps,
    stages,
    monkeypatch,
):
    candidate = candidate_factory(in_progress_steps)
    monkeypatch.setattr(Candidate, "STAGES", stages)
    service = service_factory(candidate)

    repository.find_with_current_recruitment_steps.return_value = candidate
    repository.save.return_value = candidate

    await service.run()

    assert candidate.status == "in_progress"
    assert candidate.recruitment_steps[0].status == "approved"
    assert candidate.recruitment_steps[1].status == "in_progress"
    assert candidate.recruitment_steps[2].status == "initialized"
