from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from recruitment_fastapi.schemas.permissions import PermissionResponseSchema


class CreateRoleSchema(BaseModel):
    name: str = Field(
        min_length=3, pattern=r"^[A-Za-z ]+$", description="Name of the role"
    )


class RoleResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    key: str
    created_at: datetime
    updated_at: datetime


class RoleWithPermissionsResponseSchema(RoleResponseSchema):
    model_config = ConfigDict(from_attributes=True)

    permissions: list[PermissionResponseSchema]
