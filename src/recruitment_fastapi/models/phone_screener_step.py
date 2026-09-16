from typing import ClassVar

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class PhoneScreenerStep(RecruitmentStep):
    __mapper_args__: ClassVar = {"polymorphic_identity": "phone_screeener_step"}
