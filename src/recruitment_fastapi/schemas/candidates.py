from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class CandidateType(str, Enum):
    ENTRY = "entry_candidate"
    MID = "mid_candidate"
    SENIOR = "senior_candidate"


class CreateCandidateSchema(BaseModel):
    name: str = Field(min_length=3, max_length=26, description="Name of the candidate")
    email: EmailStr = Field(description="Email of the candidate")
    phone: PhoneNumber = Field(description="Phone number of the candidate")
    experience: int = Field(ge=0, le=100, description="Experience of the candidate")


class CandidateResponseSchema(CreateCandidateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: CandidateType
    created_at: datetime
    updated_at: datetime
