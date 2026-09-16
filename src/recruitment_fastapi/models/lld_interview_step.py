from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class LldInterviewStep(RecruitmentStep):
    __mapper_args__: ClassVar = {"polymorphic_identity": "lld_interview_step"}
