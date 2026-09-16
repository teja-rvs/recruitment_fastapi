from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class BackgroundVerificationStep(RecruitmentStep):
    __mapper_args__: ClassVar = {"polymorphic_identity": "background_verification_step"}
