import pytest

from recruitment_fastapi.models import HldInterviewStep, LldInterviewStep

pytestmark = pytest.mark.unit


def test_allowed_roles():
    assert HldInterviewStep.allowed_roles() == ["staff_engineer"]


def test_prerequisite():
    assert HldInterviewStep.prerequisite() == [LldInterviewStep]
