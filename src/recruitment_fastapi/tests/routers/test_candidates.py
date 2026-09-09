import random

import pytest
from faker import Faker

fake = Faker()


@pytest.fixture
def valid_candidate_payload():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": f"+9199999{random.randint(9999, 99999)}",
        "experience": random.randint(0, 10),
    }


def _assert_validation_error(response, field: str) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", field] for error in errors), (
        f"Expected validation error for field '{field}'"
    )


def test_successful_candidate_registration(client, valid_candidate_payload):
    response = client.post("/candidates/register", json=valid_candidate_payload)
    data = response.json()

    assert response.status_code == 200

    assert data["name"] == valid_candidate_payload["name"]
    assert data["email"] == valid_candidate_payload["email"]
    assert data["phone"].startswith("tel:+91-")
    assert data["experience"] == valid_candidate_payload["experience"]


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("name", "Q" * 101),  # Too long
        ("name", "QE"),  # Too short
        ("email", "test@example@com"),  # Invalid format
        ("phone", "1234567890"),  # Invalid format
        ("experience", -5),  # Invalid experience
    ],
)
def test_candidate_registration_invalid_field(
    client, valid_candidate_payload, field: str, invalid_value: str
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


def test_candidate_registration_duplicate_email(client, valid_candidate_payload):
    response = client.post("/candidates/register", json=valid_candidate_payload)

    assert response.status_code == 200

    response = client.post("/candidates/register", json=valid_candidate_payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already taken"


def test_candidate_registration_duplicate_phone(client, valid_candidate_payload):
    response = client.post("/candidates/register", json=valid_candidate_payload)

    assert response.status_code == 200

    payload = {**valid_candidate_payload, "email": "new@example.com"}
    response = client.post("/candidates/register", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Phone already taken"
