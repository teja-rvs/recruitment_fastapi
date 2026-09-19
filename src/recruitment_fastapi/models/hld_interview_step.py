from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class HldInterviewStep(RecruitmentStep):
    STEP_TYPE: ClassVar = "hld_interview_step"

    __mapper_args__: ClassVar = {"polymorphic_identity": STEP_TYPE}
