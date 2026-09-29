from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from recruitment_fastapi.database import engine
from recruitment_fastapi.errors.duplicate_resource_error import DuplicateResourceError
from recruitment_fastapi.errors.invalid_state_error import InvalidStateError
from recruitment_fastapi.errors.resource_not_found_error import ResourceNotFoundError
from recruitment_fastapi.routers.auth import router as auth_router
from recruitment_fastapi.routers.candidates import router as candidates_router
from recruitment_fastapi.routers.permissions import router as permissions_router
from recruitment_fastapi.routers.recruitment_steps import (
    router as recruitment_steps_router,
)
from recruitment_fastapi.routers.roles import router as roles_router
from recruitment_fastapi.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Recruitment API", lifespan=lifespan)
app.include_router(candidates_router)
app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(permissions_router)
app.include_router(recruitment_steps_router)


def _is_unique_violation(exc: IntegrityError) -> bool:
    orig = exc.orig
    pgcode = getattr(orig, "pgcode", None) or getattr(orig, "sqlstate", None)
    if pgcode == "23505":
        return True
    return orig is not None and orig.__class__.__name__ in {
        "UniqueViolation",
        "UniqueViolationError",
    }


@app.exception_handler(IntegrityError)
def integrity_error_handler(_request: Request, exc: IntegrityError) -> JSONResponse:
    if _is_unique_violation(exc):
        return JSONResponse(
            status_code=409,
            content={"detail": "A record with the value already exists"},
        )
    return JSONResponse(
        status_code=400,
        content={"detail": "Request could not be completed"},
    )


@app.exception_handler(DuplicateResourceError)
def duplicate_resource_handler(
    _request: Request, exc: DuplicateResourceError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ResourceNotFoundError)
def resource_not_found_handler(
    _request: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidStateError)
def invalid_state_handler(_request: Request, exc: InvalidStateError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to the Recruitment FastAPI application!"}
