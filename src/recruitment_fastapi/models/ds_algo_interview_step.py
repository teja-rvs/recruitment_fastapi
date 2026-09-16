from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class DsAlgoInterviewStep(RecruitmentStep):
    __mapper_args__: ClassVar = {"polymorphic_identity": "ds_algo_interview_step"}
