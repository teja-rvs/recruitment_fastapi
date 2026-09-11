from unittest.mock import AsyncMock

import pytest

from recruitment_fastapi.models import (
    EntryCandidate,
    MidCandidate,
    SeniorCandidate,
)
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.schemas.candidates import CreateCandidateSchema
from recruitment_fastapi.services.candidate import CandidateService

pytestmark = pytest.mark.unit


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=CandidateRepository)


@pytest.fixture
def service(repository: AsyncMock) -> CandidateService:
    return CandidateService(repository)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("experience", "expected_class"),
    [
        pytest.param(0, EntryCandidate, id="entry-min"),
        pytest.param(3, EntryCandidate, id="entry-max"),
        pytest.param(4, MidCandidate, id="mid-min"),
        pytest.param(6, MidCandidate, id="mid-max"),
        pytest.param(7, SeniorCandidate, id="senior-min"),
    ],
)
async def test_create_candidate(
    service: CandidateService,
    repository: AsyncMock,
    experience: int,
    expected_class: type,
):
    payload = CreateCandidateSchema(
        name="Candidate",
        email="candidate@example.com",
        phone="+919999999999",
        experience=experience,
    )

    repository.create.return_value = expected_class(**payload.model_dump())

    result = await service.create_candidate(payload)

    assert isinstance(result, expected_class)

    repository.create.assert_awaited_once()

    created_candidate = repository.create.call_args.args[0]

    assert isinstance(created_candidate, expected_class)
    assert created_candidate.name == payload.name
    assert created_candidate.email == payload.email
    assert created_candidate.phone == payload.phone
    assert created_candidate.experience == payload.experience
