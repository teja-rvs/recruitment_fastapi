from unittest.mock import patch

import pytest

from recruitment_fastapi.models.candidate import Candidate
from recruitment_fastapi.states.candidate_status import CandidateStatusMachine

pytestmark = pytest.mark.unit


def test_initial_status():
    candidate = Candidate()

    assert candidate.status == CandidateStatusMachine.initial_state.value


def test_recruit():
    candidate = Candidate()

    with patch.object(candidate.status_machine, "recruit") as recruit:
        candidate.recruit()

    recruit.assert_called_once()


def test_reject():

    candidate = Candidate()
    with patch.object(candidate.status_machine, "reject") as reject:
        candidate.reject()

    reject.assert_called_once()
