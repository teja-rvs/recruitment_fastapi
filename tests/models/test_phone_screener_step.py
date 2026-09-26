import pytest

from recruitment_fastapi.models.phone_screener_step import PhoneScreenerStep

pytestmark = pytest.mark.unit


def test_allowed_roles():
    assert PhoneScreenerStep.allowed_roles() == ["recruiter"]
