import pytest

from recruitment_fastapi.models import DsAlgoInterviewStep, LldInterviewStep

pytestmark = pytest.mark.unit


def test_allowed_roles():
    assert LldInterviewStep.allowed_roles() == ["senior_engineer", "staff_engineer"]


def test_prerequisite():
    assert LldInterviewStep.prerequisite() == [DsAlgoInterviewStep]
