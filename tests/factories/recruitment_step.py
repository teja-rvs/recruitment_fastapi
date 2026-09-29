from recruitment_fastapi.models import (
    BackgroundVerificationStep,
    DsAlgoInterviewStep,
    HldInterviewStep,
    LldInterviewStep,
    PhoneScreenerStep,
    RecruitmentStep,
)

from .base import BaseTestFactory


class RecruitmentStepFactory(BaseTestFactory[RecruitmentStep]):
    __model__ = RecruitmentStep
    interview_date = None
    feedback = None


class PhoneScreenerStepFactory(RecruitmentStepFactory):
    __model__ = PhoneScreenerStep


class DsAlgoInterviewStepFactory(RecruitmentStepFactory):
    __model__ = DsAlgoInterviewStep


class LldInterviewStepFactory(RecruitmentStepFactory):
    __model__ = LldInterviewStep


class HldInterviewStepFactory(RecruitmentStepFactory):
    __model__ = HldInterviewStep


class BackgroundVerificationStepFactory(RecruitmentStepFactory):
    __model__ = BackgroundVerificationStep
