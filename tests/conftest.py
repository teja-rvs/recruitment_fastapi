from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from tests.database_config import resolve_test_database_url

_monkeypatch = pytest.MonkeyPatch()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ALEMBIC_INI = PROJECT_ROOT / "src" / "recruitment_fastapi" / "alembic.ini"


def pytest_configure(config: pytest.Config) -> None:
    database_url = resolve_test_database_url(require_test_database=True)

    # Set environment BEFORE Alembic runs.
    _monkeypatch.setenv(
        "DATABASE_URL",
        database_url,
    )

    _monkeypatch.setenv(
        "SECRET_KEY",
        "TEST_SECRET_KEY",
    )

    _run_migrations()


def _run_migrations() -> None:
    alembic_config = Config(str(ALEMBIC_INI))

    command.upgrade(
        alembic_config,
        "head",
    )


def pytest_unconfigure(config: pytest.Config) -> None:
    _monkeypatch.undo()
