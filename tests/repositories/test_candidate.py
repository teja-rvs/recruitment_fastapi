from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from psycopg.errors import NotNullViolation, UniqueViolation
from sqlalchemy.exc import IntegrityError

from recruitment_fastapi.errors.duplicate_resource_error import DuplicateResourceError
from recruitment_fastapi.models.candidate import Candidate
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
    mock_session = AsyncMock()
    mock_session.add = Mock()
    mock_session.refresh = AsyncMock()
    return mock_session


@pytest.fixture
def repository(session) -> CandidateRepository:
    return CandidateRepository(session)


@pytest.fixture
def candidate():
    return Candidate(
        name="Candidate", email="candidate@example.com", phone="1234567890"
    )


@pytest.mark.asyncio
async def test_create_successful(repository, session, candidate):
    await repository.create(candidate)

    session.add.assert_called_once_with(candidate)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(candidate)


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
