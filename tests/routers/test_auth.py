from collections.abc import Callable

import pytest
from jose import jwt

from recruitment_fastapi.services.token import ALGORITHM, SECRET_KEY

pytestmark = pytest.mark.integration


@pytest.fixture
def signup_payload_factory() -> Callable[..., dict]:
    def _make(**overrides):
        payload = {
            "email": "candidate@example.com",
            "password": "password",
            "password_confirmation": "password",
        }
        payload.update(overrides)
        return payload

    return _make


def _assert_access_token(response) -> dict:
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    assert isinstance(token, str)
    assert token

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["user_id"] is not None
    return decoded


def test_successful_signup(client, signup_payload_factory):
    response = client.post("/auth/signup", json=signup_payload_factory())

    _assert_access_token(response)


def test_signup_with_exisiting_email(client, signup_payload_factory):
    payload = signup_payload_factory()
    client.post("/auth/signup", json=payload)

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 400

    data = response.json()
    assert data["detail"] == "Email already registered"


def test_successful_login(client, signup_payload_factory):
    payload = signup_payload_factory()
    client.post("/auth/signup", json=payload)
    response = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )

    _assert_access_token(response)


def test_failed_login(client, signup_payload_factory):
    payload = signup_payload_factory()
    response = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Incorrect email or password"
