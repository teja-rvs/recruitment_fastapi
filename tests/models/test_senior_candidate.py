import pytest

from recruitment_fastapi.models import (
    BackgroundVerificationStep,
    Candidate,
    DsAlgoInterviewStep,
    LldInterviewStep,
    MidCandidate,
    PhoneScreenerStep,
)
from recruitment_fastapi.models.recruitment_stage import RecruitmentStage

pytestmark = pytest.mark.unit


def test_candidate_type():
    assert MidCandidate.CANDIDATE_TYPE == "mid_candidate"


def test_recruitment_steps():
    assert MidCandidate.RECRUITMENT_STEPS == [
        PhoneScreenerStep,
        DsAlgoInterviewStep,
        LldInterviewStep,
        BackgroundVerificationStep,
    ]


def test_stages():
    assert MidCandidate.STAGES == (
        RecruitmentStage((PhoneScreenerStep,)),
        RecruitmentStage((DsAlgoInterviewStep,)),
        RecruitmentStage((LldInterviewStep,)),
        RecruitmentStage((BackgroundVerificationStep,)),
    )


def test_is_candidate():
    candidate = MidCandidate()

    assert isinstance(candidate, Candidate)
