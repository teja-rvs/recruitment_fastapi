from datetime import datetime

from pydantic import BaseModel, ConfigDict

from recruitment_fastapi.schemas.roles import RoleResponseSchema


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime
    updated_at: datetime


class UserWithRolesResponseSchema(UserResponseSchema):
    model_config = ConfigDict(from_attributes=True)

    roles: list[RoleResponseSchema]
