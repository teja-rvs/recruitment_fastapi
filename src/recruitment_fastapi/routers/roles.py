from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import Field

from recruitment_fastapi.dependencies.permissions import require_permission
from recruitment_fastapi.dependencies.services import (
    PermissionServiceDep,
    RoleServiceDep,
)
from recruitment_fastapi.schemas.roles import (
    CreateRoleSchema,
    RoleResponseSchema,
    RoleWithPermissionsResponseSchema,
)

router = APIRouter(
    prefix="/admin/roles",
    tags=["roles"],
    dependencies=[Depends(require_permission("roles:access"))],
)

RoleIdPath = Annotated[int, Path(ge=1)]


@router.get(
    "/",
    dependencies=[Depends(require_permission("roles:view"))],
)
async def get_roles(service: RoleServiceDep) -> list[RoleResponseSchema]:
    return await service.all()


@router.post(
    "/",
    dependencies=[Depends(require_permission("roles:create"))],
)
async def create_role(
    role: CreateRoleSchema, service: RoleServiceDep
) -> RoleResponseSchema:
    created = await service.create(role)
    if created is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role exists")
    return created


@router.post(
    "/{id}/assign_permissions",
    dependencies=[Depends(require_permission("roles:assign_permissions"))],
)
async def assign_permissions(
    id: RoleIdPath,
    permission_ids: Annotated[list[int], Field(min_length=1), Body()],
    role_service: RoleServiceDep,
    permission_service: PermissionServiceDep,
) -> RoleWithPermissionsResponseSchema:
    role = await role_service.find_with_permissions(id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    permissions = await permission_service.get_permissions(permission_ids)

    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide correct permission ids",
        )

    return await role_service.assign_permissions(role, permissions)
