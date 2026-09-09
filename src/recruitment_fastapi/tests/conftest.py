import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from recruitment_fastapi.database import get_session
from recruitment_fastapi.main import app

TEST_ENV_FILE = Path(__file__).parent / ".env.test"
load_dotenv(TEST_ENV_FILE, override=True)

DATABASE_URL = os.environ["DATABASE_URL"]

test_engine = create_async_engine(DATABASE_URL)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
