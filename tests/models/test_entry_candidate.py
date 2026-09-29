import pytest

from recruitment_fastapi.models import (
    BackgroundVerificationStep,
    Candidate,
    DsAlgoInterviewStep,
    EntryCandidate,
    PhoneScreenerStep,
)
from recruitment_fastapi.models.recruitment_stage import RecruitmentStage

pytestmark = pytest.mark.unit


def test_candidate_type():
    assert EntryCandidate.CANDIDATE_TYPE == "entry_candidate"


def test_recruitment_steps():
    assert EntryCandidate.RECRUITMENT_STEPS == [
        PhoneScreenerStep,
        DsAlgoInterviewStep,
        BackgroundVerificationStep,
    ]


def test_stages():
    assert EntryCandidate.STAGES == (
        RecruitmentStage((PhoneScreenerStep,)),
        RecruitmentStage((DsAlgoInterviewStep,)),
        RecruitmentStage((BackgroundVerificationStep,)),
    )


def test_is_candidate():
    candidate = EntryCandidate()

    assert isinstance(candidate, Candidate)
