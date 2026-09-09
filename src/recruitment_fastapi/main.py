from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from recruitment_fastapi import models
from recruitment_fastapi.database import Base, engine
from recruitment_fastapi.routers.candidates import router as candidates_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(title="Recruitment API", lifespan=lifespan)
app.include_router(candidates_router)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: InterruptedError):
    return JSONResponse(
        status_code=409, content={"detail": "A record with the value already exists"}
    )


@app.get("/")
def root():
    return {"message": "Welcome to the Recruitment FastAPI application!"}
