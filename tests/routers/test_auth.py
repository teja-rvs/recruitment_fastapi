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


def _assert_access_token(response, *, user_id: int | None = None) -> dict:
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    assert isinstance(token, str)
    assert data["token_type"] == "bearer"
    assert "password" not in data
    assert "password_hash" not in data

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert isinstance(decoded["user_id"], int)
    if user_id is not None:
        assert decoded["user_id"] == user_id
    return decoded


def _assert_validation_error(response, loc: tuple[str, ...]) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(tuple(error["loc"]) == loc for error in errors)


def test_successful_signup(client, signup_payload_factory):
    payload = signup_payload_factory()

    response = client.post("/auth/signup", json=payload)

    decoded = _assert_access_token(response)

    login = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    _assert_access_token(login, user_id=decoded["user_id"])


def test_signup_with_existing_email(client, signup_payload_factory):
    payload = signup_payload_factory()
    client.post("/auth/signup", json=payload)

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.parametrize(
    ("payload", "loc"),
    [
        pytest.param(
            {
                "email": "not-an-email",
                "password": "password",
                "password_confirmation": "password",
            },
            ("body", "email"),
            id="invalid-email",
        ),
        pytest.param(
            {
                "email": "candidate@example.com",
                "password": "short",
                "password_confirmation": "short",
            },
            ("body", "password"),
            id="password-too-short",
        ),
        pytest.param(
            {
                "email": "candidate@example.com",
                "password": "a" * 101,
                "password_confirmation": "a" * 101,
            },
            ("body", "password"),
            id="password-too-long",
        ),
        pytest.param(
            {
                "email": "candidate@example.com",
                "password": "password",
                "password_confirmation": "different",
            },
            ("body",),
            id="password-mismatch",
        ),
        pytest.param(
            {"password": "password", "password_confirmation": "password"},
            ("body", "email"),
            id="missing-email",
        ),
        pytest.param(
            {"email": "candidate@example.com", "password_confirmation": "password"},
            ("body", "password"),
            id="missing-password",
        ),
        pytest.param(
            {"email": "candidate@example.com", "password": "password"},
            ("body", "password_confirmation"),
            id="missing-password-confirmation",
        ),
    ],
)
def test_signup_rejects_invalid_payload(client, payload, loc):
    response = client.post("/auth/signup", json=payload)

    _assert_validation_error(response, loc)


def test_successful_login(client, signup_payload_factory):
    payload = signup_payload_factory()
    signup = client.post("/auth/signup", json=payload)
    user_id = _assert_access_token(signup)["user_id"]

    response = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )

    _assert_access_token(response, user_id=user_id)


@pytest.mark.parametrize(
    "credentials",
    [
        pytest.param(
            {"email": "candidate@example.com", "password": "wrong-password"},
            id="wrong-password",
        ),
        pytest.param(
            {"email": "missing@example.com", "password": "password"},
            id="unknown-email",
        ),
    ],
)
def test_login_rejects_invalid_credentials(client, signup_payload_factory, credentials):
    client.post("/auth/signup", json=signup_payload_factory())

    response = client.post("/auth/login", json=credentials)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.parametrize(
    ("payload", "loc"),
    [
        pytest.param(
            {"email": "not-an-email", "password": "password"},
            ("body", "email"),
            id="invalid-email",
        ),
        pytest.param(
            {"email": "candidate@example.com", "password": "short"},
            ("body", "password"),
            id="password-too-short",
        ),
        pytest.param(
            {"email": "candidate@example.com", "password": "a" * 101},
            ("body", "password"),
            id="password-too-long",
        ),
        pytest.param(
            {"password": "password"},
            ("body", "email"),
            id="missing-email",
        ),
        pytest.param(
            {"email": "candidate@example.com"},
            ("body", "password"),
            id="missing-password",
        ),
    ],
)
def test_login_rejects_invalid_payload(client, payload, loc):
    response = client.post("/auth/login", json=payload)

    _assert_validation_error(response, loc)
