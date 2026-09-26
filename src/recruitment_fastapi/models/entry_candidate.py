from typing import ClassVar

from recruitment_fastapi.models.background_verification_step import (
    BackgroundVerificationStep,
)
from recruitment_fastapi.models.candidate import Candidate
from recruitment_fastapi.models.ds_algo_interview_step import DsAlgoInterviewStep
from recruitment_fastapi.models.phone_screener_step import PhoneScreenerStep
from recruitment_fastapi.models.recruitment_stage import RecruitmentStage


class EntryCandidate(Candidate):
    RECRUITMENT_STEPS: ClassVar = [
        PhoneScreenerStep,
        DsAlgoInterviewStep,
        BackgroundVerificationStep,
    ]

    STAGES: ClassVar = (
        RecruitmentStage((PhoneScreenerStep,)),
        RecruitmentStage((DsAlgoInterviewStep,)),
        RecruitmentStage((BackgroundVerificationStep,)),
    )

    CANDIDATE_TYPE: ClassVar = "entry_candidate"

    __mapper_args__: ClassVar = {"polymorphic_identity": CANDIDATE_TYPE}
