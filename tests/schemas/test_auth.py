import pytest

from recruitment_fastapi.schemas.auth import SignUpSchema

pytestmark = pytest.mark.unit


def test_sign_up_schema_password_mismatch():
    with pytest.raises(
        ValueError, match="Password and Password confirmation does not match"
    ):
        SignUpSchema(
            email="test@example.com",
            password="password",
            password_confirmation="mismatch",
        )
