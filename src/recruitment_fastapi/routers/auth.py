from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from recruitment_fastapi.database import SessionDep
from recruitment_fastapi.repositories.user import UserRepository
from recruitment_fastapi.schemas.auth import (
    LoginSchema,
    SignUpSchema,
    TokenResponseSchema,
)
from recruitment_fastapi.services.login import LoginService
from recruitment_fastapi.services.sign_up import SignUpService
from recruitment_fastapi.services.token import TokenService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_sign_up_service(session: SessionDep) -> SignUpService:
    return SignUpService(UserRepository(session))


def get_login_service(session: SessionDep) -> LoginService:
    return LoginService(UserRepository(session))


def get_token_service() -> TokenService:
    return TokenService()


SignUpServiceDep = Annotated[SignUpService, Depends(get_sign_up_service)]
LoginServiceDep = Annotated[LoginService, Depends(get_login_service)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


@router.post("/signup")
async def signup(
    data: SignUpSchema,
    sign_up_service: SignUpServiceDep,
    token_service: TokenServiceDep,
) -> TokenResponseSchema:
    user = await sign_up_service.sign_up(data)

    return TokenResponseSchema(access_token=token_service.encode({"user_id": user.id}))


@router.post("/login")
async def login(
    data: LoginSchema,
    login_service: LoginServiceDep,
    token_service: TokenServiceDep,
) -> TokenResponseSchema:
    user = await login_service.authenticate(data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return TokenResponseSchema(access_token=token_service.encode({"user_id": user.id}))
