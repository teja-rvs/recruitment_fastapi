from unittest.mock import ANY, Mock

import pytest

from recruitment_fastapi.models import RecruitmentStep, User
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def repository(session) -> RecruitmentStepRepository:
    return RecruitmentStepRepository(session)


@pytest.fixture
def recruitment_step():
    return RecruitmentStep(candidate_id=1)


@pytest.mark.asyncio
async def test_create(repository, session, recruitment_step):
    result = await repository.create(recruitment_step)

    session.add.assert_called_once_with(recruitment_step)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(recruitment_step)
    assert result is recruitment_step


@pytest.mark.asyncio
async def test_create_all(repository, session):
    steps = []
    for i in range(3):
        steps.append(RecruitmentStep(candidate_id=i))

    result = await repository.create_all(steps)

    assert result is steps
    session.add_all.assert_called_once_with(steps)
    session.commit.assert_awaited_once()


@pytest.fixture
def recruitment_steps():
    return [
        RecruitmentStep(id=1, candidate_id=1),
        RecruitmentStep(id=2, candidate_id=1),
        RecruitmentStep(id=3, candidate_id=1),
    ]


@pytest.mark.asyncio
async def test_find_by_candidate(session, repository, recruitment_steps):
    execute_result = Mock()

    execute_result.scalars.return_value.all.return_value = recruitment_steps
    session.execute.return_value = execute_result

    result = await repository.find_by_candidate(1)

    session.execute.assert_awaited_once()
    assert result == recruitment_steps


@pytest.mark.asyncio
async def test_find_return_recruitment_step(session, repository, recruitment_step):
    session.get.return_value = recruitment_step

    result = await repository.find(recruitment_step.id)

    assert result is recruitment_step
    session.get.assert_awaited_once_with(
        RecruitmentStep, recruitment_step.id, options=ANY
    )


@pytest.mark.asyncio
async def test_find_return_none(session, repository):
    session.get.return_value = None

    result = await repository.find(1)

    assert result is None
    session.get.assert_awaited_once_with(RecruitmentStep, 1, options=ANY)


@pytest.fixture
def user():
    return User(id=1)


@pytest.mark.asyncio
async def test_allowed_interviewer_return_user_id(session, repository, user):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = user.id
    session.execute.return_value = execute_result

    result = await repository.allowed_interviewer(user.id, ["test_role"])

    assert result == user.id
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_allowed_interviewer_return_none(session, repository):
    execute_result = Mock()
    execute_result.scalar_one_or_none.return_value = None
    session.execute.return_value = execute_result

    result = await repository.allowed_interviewer(1, ["test_role"])

    assert result is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_save(session, repository, recruitment_step):
    result = await repository.save(recruitment_step)

    assert result is recruitment_step
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(recruitment_step)


@pytest.mark.asyncio
async def test_all(session, repository, recruitment_steps):
    execute_result = Mock()
    execute_result.scalars.return_value.all.return_value = recruitment_steps
    session.execute.return_value = execute_result

    result = await repository.all()

    session.execute.assert_awaited_once()
    execute_result.scalars.assert_called_once_with()
    execute_result.scalars.return_value.all.assert_called_once_with()
    assert result is recruitment_steps


@pytest.mark.asyncio
async def test_save_all(session, repository):
    await repository.save_all()

    session.commit.assert_awaited_once()
