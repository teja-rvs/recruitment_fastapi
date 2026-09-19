from collections.abc import Callable

import phonenumbers
import pytest
from phonenumbers import PhoneNumberFormat

from recruitment_fastapi.models import EntryCandidate, MidCandidate, SeniorCandidate
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository

pytestmark = pytest.mark.integration

_CANDIDATE_BY_TYPE = {
    EntryCandidate.CANDIDATE_TYPE: EntryCandidate,
    MidCandidate.CANDIDATE_TYPE: MidCandidate,
    SeniorCandidate.CANDIDATE_TYPE: SeniorCandidate,
}


@pytest.fixture
def candidate_payload_factory() -> Callable[..., dict]:
    counter = 0

    def _make(**overrides):
        nonlocal counter
        counter += 1
        payload = {
            "name": "Ada Lovelace",
            "email": f"candidate{counter}@example.com",
            "phone": f"+91900000{counter:04d}",
            "experience": 4,
        }
        payload.update(overrides)
        return payload

    return _make


@pytest.fixture
def valid_candidate_payload(candidate_payload_factory: Callable[..., dict]) -> dict:
    return candidate_payload_factory()


def _assert_validation_error(response, field: str) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", field] for error in errors), (
        f"Expected validation error for field '{field}'"
    )


def _register_candidate(client, payload: dict):
    response = client.post("/candidates/register", json=payload)
    assert response.status_code == 200
    return response


def _phone_uri(value: str) -> str:
    parsed = phonenumbers.parse(value, None)
    return phonenumbers.format_number(parsed, PhoneNumberFormat.RFC3966)


@pytest.mark.parametrize(
    ("field", "value", "candidate_type"),
    [
        pytest.param("experience", 1, EntryCandidate.CANDIDATE_TYPE),
        pytest.param("experience", 4, MidCandidate.CANDIDATE_TYPE),
        pytest.param("experience", 10, SeniorCandidate.CANDIDATE_TYPE),
    ],
)
def test_successful_candidate_registration(
    client, db_session, valid_candidate_payload, field, value, candidate_type
):
    payload = {**valid_candidate_payload, field: value}
    response = client.post("/candidates/register", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["phone"] == _phone_uri(payload["phone"])
    assert data["experience"] == payload["experience"]
    assert data["type"] == candidate_type

    expected_step_types = [
        step_cls.STEP_TYPE
        for step_cls in _CANDIDATE_BY_TYPE[candidate_type].RECRUITMENT_STEPS
    ]

    async def fetch_step_types(session):
        steps = await RecruitmentStepRepository(session).find_by_candidate(data["id"])
        return [step.type for step in steps]

    assert sorted(db_session(fetch_step_types)) == sorted(expected_step_types)


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        pytest.param("name", "Q" * 101, id="name-too-long"),
        pytest.param("name", "QE", id="name-too-short"),
        pytest.param("email", "test@example@com", id="email-invalid-format"),
        pytest.param("phone", "1234567890", id="phone-invalid-format"),
        pytest.param("experience", -5, id="experience-negative"),
    ],
)
def test_candidate_registration_invalid_field(
    client, valid_candidate_payload, field: str, invalid_value: str | int
):
    payload = {**valid_candidate_payload, field: invalid_value}
    response = client.post("/candidates/register", json=payload)

    _assert_validation_error(response, field)


def test_candidate_registration_with_missing_fields(client):
    response = client.post("/candidates/register", json={})

    assert response.status_code == 422
    errors = response.json()["detail"]

    required_fields = ["name", "email", "phone", "experience"]
    for field in required_fields:
        assert any(error["loc"] == ["body", field] for error in errors), (
            f"Expected validation error for missing field '{field}'"
        )


def test_candidate_registration_duplicate_email(client, candidate_payload_factory):
    payload = candidate_payload_factory()
    _register_candidate(client, payload)

    duplicate = candidate_payload_factory(email=payload["email"])
    response = client.post("/candidates/register", json=duplicate)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already taken"


def test_candidate_registration_duplicate_phone(client, candidate_payload_factory):
    payload = candidate_payload_factory()
    _register_candidate(client, payload)

    duplicate = candidate_payload_factory(phone=payload["phone"])
    response = client.post("/candidates/register", json=duplicate)

    assert response.status_code == 409
    assert response.json()["detail"] == "Phone already taken"
