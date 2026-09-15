import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def valid_signup_payload() -> dict:
    return {
        "email": "candidate@example.com",
        "password": "password",
        "password_confirmation": "password",
    }


@pytest.fixture
def valid_login_payload() -> dict:
    return {"email": "candidate@example.com", "password": "password"}


def test_successful_signup(client, valid_signup_payload):
    response = client.post("/auth/signup", json=valid_signup_payload)

    assert response.status_code == 200

    assert "access_token" in response.json()


def test_successful_login(client, valid_login_payload, valid_signup_payload):
    client.post("/auth/signup", json=valid_signup_payload)
    response = client.post("/auth/login", json=valid_login_payload)

    assert response.status_code == 200

    assert "access_token" in response.json()


def test_failed_login(client, valid_login_payload):
    response = client.post("/auth/login", json=valid_login_payload)

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Incorrect email or password"
