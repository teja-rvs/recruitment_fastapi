from collections.abc import Iterator

import anyio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from tests.database_config import resolve_test_database_url


@pytest.fixture(scope="session")
def test_engine() -> Iterator[AsyncEngine]:
    database_url = resolve_test_database_url(require_test_database=True)
    engine = create_async_engine(database_url)
    try:
        yield engine
    finally:
        anyio.run(engine.dispose)


@pytest.fixture
def client(test_engine: AsyncEngine) -> Iterator[TestClient]:
    from recruitment_fastapi.database import get_session
    from recruitment_fastapi.main import app

    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_session():
        async with session_factory() as session:
            yield session

    anyio.run(_truncate_candidates, test_engine)
    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        anyio.run(_truncate_candidates, test_engine)


async def _truncate_candidates(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("TRUNCATE TABLE candidates RESTART IDENTITY CASCADE")
        )
