from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreatePermissionSchema(BaseModel):
    model: str = Field(min_length=3, description="Name of the model")
    permission: str = Field(min_length=3, description="Permission for the model")


class PermissionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime
