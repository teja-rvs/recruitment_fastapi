from typing import ClassVar

from recruitment_fastapi.models.background_verification_step import (
    BackgroundVerificationStep,
)
from recruitment_fastapi.models.candidate import Candidate
from recruitment_fastapi.models.ds_algo_interview_step import DsAlgoInterviewStep
from recruitment_fastapi.models.lld_interview_step import LldInterviewStep
from recruitment_fastapi.models.phone_screener_step import PhoneScreenerStep


class MidCandidate(Candidate):
    RECRUITMENT_STEPS: ClassVar = [
        PhoneScreenerStep,
        DsAlgoInterviewStep,
        LldInterviewStep,
        BackgroundVerificationStep,
    ]

    CANDIDATE_TYPE: ClassVar = "mid_candidate"

    __mapper_args__: ClassVar = {"polymorphic_identity": CANDIDATE_TYPE}
