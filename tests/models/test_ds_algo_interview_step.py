import pytest

from recruitment_fastapi.models.ds_algo_interview_step import DsAlgoInterviewStep

pytestmark = pytest.mark.unit


def test_allowed_roles():
    assert DsAlgoInterviewStep.allowed_roles() == [
        "engineer",
        "senior_engineer",
        "staff_engineer",
    ]
