from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from recruitment_fastapi.schemas.candidates import CandidateResponseSchema
from recruitment_fastapi.schemas.users import UserResponseSchema


class AssignInterviewerSchema(BaseModel):
    interviewer_id: int | None = Field(
        default=None, gt=0, description="ID of the interviewer"
    )
    interview_date: date | None = Field(
        default=None, description="Interview date of the recruitment step"
    )

    @field_validator("interview_date")
    @classmethod
    def validate_interviewer_date(cls, value: date | None) -> date | None:
        if value is None:
            return value

        today_utc = datetime.now(tz=UTC).date()

        if value <= today_utc:
            raise ValueError("Interview date must be in future")
        else:
            return value


class RecruitmentStepResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    status: str
    feedback: str | None = None

    candidate: CandidateResponseSchema | None = None

    interview_date: date | None = None
    interviewer: UserResponseSchema | None = None

    created_at: datetime
    updated_at: datetime


class ReviewSchema(BaseModel):
    review: str = Field(min_length=3, description="The review of the interview")
