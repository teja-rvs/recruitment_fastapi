import pytest
from faker import Faker

fake = Faker()


@pytest.fixture
def valid_candidate_payload():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": f"+91{fake.msisdn()[3:]}",
        "role": "junior",
    }


def _assert_validation_error(response, field: str) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", field] for error in errors), (
        f"Expected validation error for field '{field}'"
    )


# FIX 1: Inject the fixture as an argument
def test_successful_candidate_registration(client, valid_candidate_payload):
    response = client.post("/candidates/register", json=valid_candidate_payload)
    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "Candidate registered successfully"

    candidate = data["candidate"]

    assert candidate["name"] == valid_candidate_payload["name"]
    assert candidate["email"] == valid_candidate_payload["email"]
    assert candidate["role"] == valid_candidate_payload["role"]
    assert candidate["phone"].startswith("tel:+91-")


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("name", "QWERTYUIOPASDFGHJKLZXCVBNM!@#$"),  # Too long
        ("name", "QE"),  # Too short
        ("email", "test@example@com"),  # Invalid format
        ("phone", "1234567890"),  # Invalid format
        ("role", "test"),  # Invalid choice
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

    required_fields = ["name", "email", "phone", "role"]
    for field in required_fields:
        assert any(error["loc"] == ["body", field] for error in errors), (
            f"Expected validation error for missing field '{field}'"
        )
