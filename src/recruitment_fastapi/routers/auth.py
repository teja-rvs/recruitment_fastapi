from fastapi import APIRouter, HTTPException, status

from recruitment_fastapi.dependencies.services import (
    LoginServiceDep,
    SignUpServiceDep,
    TokenServiceDep,
)
from recruitment_fastapi.schemas.auth import (
    LoginSchema,
    SignUpSchema,
    TokenResponseSchema,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(
    data: SignUpSchema,
    sign_up_service: SignUpServiceDep,
    token_service: TokenServiceDep,
) -> TokenResponseSchema:
    user = await sign_up_service.sign_up(data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    return TokenResponseSchema(
        access_token=await token_service.encode({"user_id": user.id})
    )


@router.post("/login")
async def login(
    data: LoginSchema,
    login_service: LoginServiceDep,
    token_service: TokenServiceDep,
) -> TokenResponseSchema:
    user = await login_service.authenticate(data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return TokenResponseSchema(
        access_token=await token_service.encode({"user_id": user.id})
    )
