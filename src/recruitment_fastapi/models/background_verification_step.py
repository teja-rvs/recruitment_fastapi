from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class BackgroundVerificationStep(RecruitmentStep):
    STEP_TYPE: ClassVar = "background_verification_step"

    __mapper_args__: ClassVar = {"polymorphic_identity": STEP_TYPE}
