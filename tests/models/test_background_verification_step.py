from unittest.mock import patch

import pytest

from recruitment_fastapi.models import BackgroundVerificationStep, HldInterviewStep

pytestmark = pytest.mark.unit


def test_allowed_roles():
    assert BackgroundVerificationStep.allowed_roles() == ["hiring_manager"]


def test_prerequisite():
    assert BackgroundVerificationStep.prerequisite() == [HldInterviewStep]


def test_submit_feedback():
    step = BackgroundVerificationStep()

    with patch.object(step.status_machine, "request_review") as request_review:
        step.submit_feedback("Test Feedback")

    assert step.feedback == "Test Feedback"
    request_review.assert_called_once()
