from unittest.mock import patch

import pytest

from recruitment_fastapi.models.recruitment_step import RecruitmentStep
from recruitment_fastapi.states.recruitment_step_status import (
    RecruitmentStepStatusMachine,
)

pytestmark = pytest.mark.unit


def test_initial_status():
    step = RecruitmentStep()

    assert step.status == RecruitmentStepStatusMachine.initial_state.value


def test_start():
    step = RecruitmentStep()

    with patch.object(step.status_machine, "start") as start:
        step.start()

    start.assert_called_once()


def test_schedule_interview():
    step = RecruitmentStep()

    with patch.object(step.status_machine, "schedule_interview") as schedule_interview:
        step.schedule_interview()

    schedule_interview.assert_called_once()


def test_interview_complete():
    step = RecruitmentStep()

    with patch.object(step.status_machine, "interview_complete") as interview_complete:
        step.interview_complete()

    interview_complete.assert_called_once()


def test_approve():
    step = RecruitmentStep()

    with patch.object(step.status_machine, "approve") as approve:
        step.approve()

    approve.assert_called_once()


def test_reject():
    step = RecruitmentStep()

    with patch.object(step.status_machine, "reject") as reject:
        step.reject()

    reject.assert_called_once()


def test_cancel():
    step = RecruitmentStep()

    with patch.object(step.status_machine, "cancel") as cancel:
        step.cancel()

    cancel.assert_called_once()
