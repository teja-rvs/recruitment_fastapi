from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from psycopg.errors import NotNullViolation, UniqueViolation
from sqlalchemy.exc import IntegrityError

from recruitment_fastapi.errors.duplicate_resource_error import DuplicateResourceError
from recruitment_fastapi.models import Candidate, RecruitmentStep
from recruitment_fastapi.repositories.candidate import CandidateRepository

pytestmark = pytest.mark.unit


class MockUniqueViolation(UniqueViolation):
    def __init__(self, message: str = "Mock Unique Violation"):
        super().__init__(message)
        self._diag = None

    @property
    def diag(self):
        return self._diag

    @diag.setter
    def diag(self, value):
        self._diag = value


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(session) -> CandidateRepository:
    return CandidateRepository(session)


@pytest.fixture
def candidate():
    return Candidate(
        id=1, name="Candidate", email="candidate@example.com", phone="1234567890"
    )


@pytest.fixture
def candidate_with_steps(candidate):
    candidate.recruitment_steps = [RecruitmentStep(id=1), RecruitmentStep(id=2)]
    return candidate


@pytest.mark.asyncio
async def test_create_successful(repository, session, candidate):
    result = await repository.create(candidate)

    session.add.assert_called_once_with(candidate)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(candidate)

    assert result is candidate


@pytest.mark.asyncio
async def test_create_duplicate_email(repository, session, candidate):
    violation = MockUniqueViolation()
    violation.diag = SimpleNamespace(constraint_name="ix_candidates_email")

    session.commit.side_effect = IntegrityError(
        statement=None, params=None, orig=violation
    )

    with pytest.raises(DuplicateResourceError, match="Email already taken"):
        await repository.create(candidate)

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_duplicate_phone(repository, session, candidate):
    violation = MockUniqueViolation()
    violation.diag = SimpleNamespace(constraint_name="ix_candidates_phone")

    session.commit.side_effect = IntegrityError(
        statement=None, params=None, orig=violation
    )

    with pytest.raises(DuplicateResourceError, match="Phone already taken"):
        await repository.create(candidate)

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_integrity_error_non_unique_violation(
    repository, session, candidate
):
    violation = Mock()
    violation.__class__ = NotNullViolation

    session.commit.side_effect = IntegrityError(
        statement=None, params=None, orig=violation
    )

    with pytest.raises(IntegrityError):
        await repository.create(candidate)

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_returns_candidate(repository, session, candidate):
    session.get.return_value = candidate

    result = await repository.find(candidate.id)

    assert result is candidate
    session.get.assert_awaited_once_with(Candidate, candidate.id)


@pytest.mark.asyncio
async def test_find_returns_none(repository, session):
    session.get.return_value = None

    result = await repository.find(1)

    assert result is None
    session.get.assert_awaited_once_with(Candidate, 1)


@pytest.mark.asyncio
async def test_find_with_current_recruitment_steps_returns_candidate(
    session, repository, candidate_with_steps
):
    result = Mock()
    result.scalar_one_or_none.return_value = candidate_with_steps
    session.execute.return_value = result

    candidate = await repository.find_with_current_recruitment_steps(
        candidate_with_steps.id
    )

    assert candidate is candidate_with_steps

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_with_current_recruitment_steps_returns_none(session, repository):
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    candidate = await repository.find_with_current_recruitment_steps(1)

    assert candidate is None

    session.execute.assert_awaited_once()
