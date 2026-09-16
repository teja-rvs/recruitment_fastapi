from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class HldInterviewStep(RecruitmentStep):
    __mapper_args__: ClassVar = {"polymorphic_identity": "hld_interview_step"}
