from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.jobs.create_recruitment_steps_for_candidate import (
    create_recruitment_steps_for_candidate,
)
from recruitment_fastapi.models.entry_candidate import EntryCandidate
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def candidate_repository() -> AsyncMock:
    return AsyncMock(spec=CandidateRepository)


@pytest.fixture
def recruitment_step_repository() -> AsyncMock:
    return AsyncMock(spec=RecruitmentStepRepository)


@pytest.fixture
def candidate():
    return EntryCandidate(id=1)


@pytest.mark.asyncio
async def test_create_recruitment_steps_for_candidate(
    candidate_repository: CandidateRepository,
    recruitment_step_repository: RecruitmentStepRepository,
    candidate: EntryCandidate,
):
    candidate_repository.find.return_value = candidate

    result = await create_recruitment_steps_for_candidate(
        1, candidate_repository, recruitment_step_repository
    )

    assert result is True

    recruitment_step_repository.create_all.assert_awaited_once()
    created_steps = recruitment_step_repository.create_all.await_args.args[0]
    assert [type(step) for step in created_steps] == list(candidate.RECRUITMENT_STEPS)
    assert all(step.candidate_id == candidate.id for step in created_steps)
