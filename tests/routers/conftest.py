from collections.abc import Awaitable, Callable, Iterator
from typing import TypeVar

import anyio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from recruitment_fastapi.database import get_session
from recruitment_fastapi.main import app
from tests.helpers.auth import auth_headers  # noqa: F401
from tests.helpers.user import create_user_with_permissions  # noqa: F401

T = TypeVar("T")


@pytest.fixture(scope="session")
def test_engine() -> Iterator[AsyncEngine]:
    from recruitment_fastapi.database import engine

    try:
        yield engine
    finally:
        anyio.run(engine.dispose)


@pytest.fixture
def session_factory(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[Callable[[AsyncSession], Awaitable[T]]], T]:
    def run(operation: Callable[[AsyncSession], Awaitable[T]]) -> T:
        async def _inner() -> T:
            async with session_factory() as session:
                return await operation(session)

        return anyio.run(_inner)

    return run


@pytest.fixture
def client(
    test_engine: AsyncEngine, session_factory: async_sessionmaker[AsyncSession]
) -> Iterator[TestClient]:
    async def override_get_session():
        async with session_factory() as session:
            yield session

    anyio.run(_truncate_tables, test_engine)
    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        anyio.run(_truncate_tables, test_engine)


async def _truncate_tables(engine: AsyncEngine) -> None:
    from recruitment_fastapi.database import Base

    table_names = ", ".join(
        f'"{table.name}"'
        for table in Base.metadata.sorted_tables
        if table.name != "alembic_version"
    )

    async with engine.begin() as connection:
        await connection.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        )


@pytest.fixture(autouse=True)
def setup_factory_sessions(session_factory: async_sessionmaker[AsyncSession]):
    from tests.factories.base import AsyncSessionPersistence, BaseTestFactory

    BaseTestFactory.__async_persistence__ = AsyncSessionPersistence(session_factory)
    yield
    BaseTestFactory.__async_persistence__ = None
