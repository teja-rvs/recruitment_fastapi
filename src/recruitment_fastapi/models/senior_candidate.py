from typing import ClassVar

from recruitment_fastapi.models import (
    BackgroundVerificationStep,
    Candidate,
    DsAlgoInterviewStep,
    HldInterviewStep,
    LldInterviewStep,
)
from recruitment_fastapi.models.phone_screener_step import PhoneScreenerStep
from recruitment_fastapi.models.recruitment_stage import RecruitmentStage


class SeniorCandidate(Candidate):
    RECRUITMENT_STEPS: ClassVar = [
        PhoneScreenerStep,
        DsAlgoInterviewStep,
        LldInterviewStep,
        HldInterviewStep,
        BackgroundVerificationStep,
    ]

    STAGES = (
        RecruitmentStage((PhoneScreenerStep,)),
        RecruitmentStage((DsAlgoInterviewStep,)),
        RecruitmentStage((LldInterviewStep,)),
        RecruitmentStage((HldInterviewStep,)),
        RecruitmentStage((BackgroundVerificationStep,)),
    )

    CANDIDATE_TYPE: ClassVar = "senior_candidate"

    __mapper_args__: ClassVar = {"polymorphic_identity": CANDIDATE_TYPE}
