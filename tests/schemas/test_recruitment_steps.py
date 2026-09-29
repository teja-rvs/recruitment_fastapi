import pytest

from recruitment_fastapi.schemas.recruitment_steps import AssignInterviewerSchema

pytestmark = pytest.mark.unit


def test_assign_interviewer_schema():
    with pytest.raises(ValueError, match="Interview date must be in future"):
        AssignInterviewerSchema(interview_date="2000-01-01")
