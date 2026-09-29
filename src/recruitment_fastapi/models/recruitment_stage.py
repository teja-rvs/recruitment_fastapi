from dataclasses import dataclass

from recruitment_fastapi.models.recruitment_step import RecruitmentStep


@dataclass(frozen=True)
class RecruitmentStage:
    steps: tuple[type[RecruitmentStep], ...]
