from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class DsAlgoInterviewStep(RecruitmentStep):
    STEP_TYPE: ClassVar = "ds_algo_interview_step"

    __mapper_args__: ClassVar = {"polymorphic_identity": STEP_TYPE}

    @classmethod
    def allowed_roles(cls):
        return ["engineer", "senior_engineer", "staff_engineer"]
