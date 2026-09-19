from unittest.mock import AsyncMock, Mock

import pytest

from recruitment_fastapi.models.recruitment_step import RecruitmentStep
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def session() -> AsyncMock:
    session = AsyncMock()
    session.add = Mock()
    session.add_all = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    return session


@pytest.fixture
def repository(session) -> RecruitmentStepRepository:
    return RecruitmentStepRepository(session)


@pytest.mark.asyncio
async def test_create(repository, session):
    step = RecruitmentStep(candidate_id=1)
    await repository.create(step)

    session.add.assert_called_once_with(step)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(step)


@pytest.mark.asyncio
async def test_create_all(repository, session):
    steps = []
    for i in range(3):
        steps.append(RecruitmentStep(candidate_id=i))

    await repository.create_all(steps)

    session.add_all.assert_called_once_with(steps)
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_candidate(session, repository):
    execute_result = Mock()

    steps = [
        RecruitmentStep(id=1, candidate_id=1),
        RecruitmentStep(id=2, candidate_id=1),
        RecruitmentStep(id=3, candidate_id=1),
    ]

    execute_result.scalars.return_value.all.return_value = steps
    session.execute.return_value = execute_result

    result = await repository.find_by_candidate(1)

    session.execute.assert_called_once()
    assert result == steps
