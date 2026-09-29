from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import Field

from recruitment_fastapi.dependencies.permissions import require_permission
from recruitment_fastapi.dependencies.services import RoleServiceDep, UserServiceDep
from recruitment_fastapi.schemas.roles import RoleResponseSchema
from recruitment_fastapi.schemas.users import (
    UserResponseSchema,
    UserWithRolesResponseSchema,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_permission("users:access"))],
)

UserIdPath = Annotated[int, Path(ge=1)]


@router.get(
    "/",
    dependencies=[Depends(require_permission("users:view"))],
)
async def get_users(user_service: UserServiceDep) -> list[UserResponseSchema]:
    return await user_service.all()


@router.get(
    "/{id}/roles",
    dependencies=[Depends(require_permission("users:view"))],
)
async def get_roles(
    id: UserIdPath, user_service: UserServiceDep
) -> list[RoleResponseSchema]:
    user = await user_service.find_with_roles(id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user.roles


@router.post(
    "/{id}/assign_roles",
    dependencies=[Depends(require_permission("users:assign_roles"))],
)
async def assign_roles(
    id: UserIdPath,
    role_ids: Annotated[list[int], Field(min_length=1), Body()],
    user_service: UserServiceDep,
    role_service: RoleServiceDep,
) -> UserWithRolesResponseSchema:
    user = await user_service.find_with_roles(id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    roles = await role_service.get_roles(role_ids)

    if roles is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide correct role ids",
        )

    updated_user = await user_service.assign_roles(user, roles)

    return UserWithRolesResponseSchema.model_validate(updated_user)
