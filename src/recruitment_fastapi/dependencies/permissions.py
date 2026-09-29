from fastapi import HTTPException, status

from recruitment_fastapi.dependencies.auth import CurrentUserDep
from recruitment_fastapi.dependencies.services import PermissionServiceDep


def require_permission(permission: str):
    async def permission_checker(
        current_user: CurrentUserDep, permission_service: PermissionServiceDep
    ):
        has_permission = await permission_service.check_permission_for_user(
            current_user.id, permission
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
            )

        return has_permission

    return permission_checker
