import pytest

from recruitment_fastapi.models import (
    BackgroundVerificationStep,
    Candidate,
    DsAlgoInterviewStep,
    HldInterviewStep,
    LldInterviewStep,
    SeniorCandidate,
)
from recruitment_fastapi.models.phone_screener_step import PhoneScreenerStep
from recruitment_fastapi.models.recruitment_stage import RecruitmentStage

pytestmark = pytest.mark.unit


def test_candidate_type():
    assert SeniorCandidate.CANDIDATE_TYPE == "senior_candidate"


def test_recruitment_steps():
    assert SeniorCandidate.RECRUITMENT_STEPS == [
        PhoneScreenerStep,
        DsAlgoInterviewStep,
        LldInterviewStep,
        HldInterviewStep,
        BackgroundVerificationStep,
    ]


def test_stages():
    assert SeniorCandidate.STAGES == (
        RecruitmentStage((PhoneScreenerStep,)),
        RecruitmentStage((DsAlgoInterviewStep,)),
        RecruitmentStage((LldInterviewStep,)),
        RecruitmentStage((HldInterviewStep,)),
        RecruitmentStage((BackgroundVerificationStep,)),
    )


def test_is_candidate():
    candidate = SeniorCandidate()

    assert isinstance(candidate, Candidate)
