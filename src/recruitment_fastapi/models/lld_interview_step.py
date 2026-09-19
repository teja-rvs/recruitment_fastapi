from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class LldInterviewStep(RecruitmentStep):
    STEP_TYPE: ClassVar = "lld_interview_step"

    __mapper_args__: ClassVar = {"polymorphic_identity": STEP_TYPE}
