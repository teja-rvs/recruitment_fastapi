from typing import ClassVar

from recruitment_fastapi.models.ds_algo_interview_step import DsAlgoInterviewStep
from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class LldInterviewStep(RecruitmentStep):
    STEP_TYPE: ClassVar = "lld_interview_step"

    __mapper_args__: ClassVar = {"polymorphic_identity": STEP_TYPE}

    @classmethod
    def allowed_roles(cls):
        return ["senior_engineer", "staff_engineer"]

    @classmethod
    def prerequisite(cls):
        return [DsAlgoInterviewStep]
