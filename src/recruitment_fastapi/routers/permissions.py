from fastapi import APIRouter, Depends, HTTPException, status

from recruitment_fastapi.dependencies.permissions import require_permission
from recruitment_fastapi.dependencies.services import PermissionServiceDep
from recruitment_fastapi.schemas.permissions import (
    CreatePermissionSchema,
    PermissionResponseSchema,
)

router = APIRouter(
    prefix="/admin/permissions",
    tags=["permissions"],
    dependencies=[Depends(require_permission("permissions:access"))],
)


@router.post(
    "/",
    dependencies=[Depends(require_permission("permissions:create"))],
)
async def create(
    permission_service: PermissionServiceDep, data: CreatePermissionSchema
) -> PermissionResponseSchema:
    permission = await permission_service.create(data)

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Permission already exists"
        )

    return permission


@router.get(
    "/",
    dependencies=[Depends(require_permission("permissions:view"))],
)
async def get_permissions(
    permission_service: PermissionServiceDep,
) -> list[PermissionResponseSchema]:
    return await permission_service.all()
