from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)
