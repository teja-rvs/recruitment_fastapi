from typing import Annotated

from fastapi import BackgroundTasks, Depends

from recruitment_fastapi.database import SessionDep
from recruitment_fastapi.repositories.candidate import CandidateRepository
from recruitment_fastapi.repositories.permission import PermissionRepository
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository
from recruitment_fastapi.repositories.role import RoleRepository
from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.services.candidate import CandidateService
from recruitment_fastapi.services.login import LoginService
from recruitment_fastapi.services.permission import PermissionService
from recruitment_fastapi.services.recruitment_step import RecruitmentStepService
from recruitment_fastapi.services.role import RoleService
from recruitment_fastapi.services.sign_up import SignUpService
from recruitment_fastapi.services.token import TokenService
from recruitment_fastapi.services.user import UserService


def get_user_service(session: SessionDep) -> UserService:
    return UserService(UserRepository(session))


def get_role_service(session: SessionDep) -> RoleService:
    return RoleService(RoleRepository(session))


def get_permission_service(session: SessionDep) -> PermissionService:
    return PermissionService(PermissionRepository(session))


def get_token_service() -> TokenService:
    return TokenService()


def get_sign_up_service(session: SessionDep) -> SignUpService:
    return SignUpService(UserRepository(session))


def get_login_service(session: SessionDep) -> LoginService:
    return LoginService(UserRepository(session))


def get_candidate_service(
    session: SessionDep, background_tasks: BackgroundTasks
) -> CandidateService:
    return CandidateService(CandidateRepository(session), background_tasks)


def get_recruitment_step_service(
    session: SessionDep, background_tasks: BackgroundTasks
) -> RecruitmentStepService:
    return RecruitmentStepService(RecruitmentStepRepository(session), background_tasks)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
SignUpServiceDep = Annotated[SignUpService, Depends(get_sign_up_service)]
LoginServiceDep = Annotated[LoginService, Depends(get_login_service)]
CandidateServiceDep = Annotated[CandidateService, Depends(get_candidate_service)]
RecruitmentStepServiceDep = Annotated[
    RecruitmentStepService, Depends(get_recruitment_step_service)
]
