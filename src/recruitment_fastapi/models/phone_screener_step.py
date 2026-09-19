from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class PhoneScreenerStep(RecruitmentStep):
    STEP_TYPE: ClassVar = "phone_screener_step"

    __mapper_args__: ClassVar = {"polymorphic_identity": STEP_TYPE}
