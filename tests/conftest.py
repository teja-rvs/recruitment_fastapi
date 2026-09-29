from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from tests.database_config import UNIT_DATABASE_URL, resolve_test_database_url

_monkeypatch = pytest.MonkeyPatch()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ALEMBIC_INI = PROJECT_ROOT / "src" / "recruitment_fastapi" / "alembic.ini"

_INTEGRATION_TEST_DIR_NAMES = frozenset({"routers"})


def _session_needs_test_database(config: pytest.Config) -> bool:
    markexpr = (config.option.markexpr or "").strip()
    if markexpr in {"unit", "not integration"}:
        return False

    args = list(config.args)
    if not args:
        return True

    return not all(_is_unit_only_arg(arg) for arg in args)


def _is_unit_only_arg(arg: str) -> bool:
    path = Path(str(arg).split("::", 1)[0]).resolve()
    parts = path.parts
    try:
        tests_index = parts.index("tests")
    except ValueError:
        return False

    if tests_index + 1 >= len(parts):
        return False

    return parts[tests_index + 1] not in _INTEGRATION_TEST_DIR_NAMES


def pytest_configure(config: pytest.Config) -> None:
    _monkeypatch.setenv("SECRET_KEY", "TEST_SECRET_KEY")

    if _session_needs_test_database(config):
        database_url = resolve_test_database_url(require_test_database=True)
        _monkeypatch.setenv("DATABASE_URL", database_url)
        _run_migrations()
        return

    _monkeypatch.setenv("DATABASE_URL", UNIT_DATABASE_URL)


def _run_migrations() -> None:
    alembic_config = Config(str(ALEMBIC_INI))

    command.upgrade(
        alembic_config,
        "head",
    )


def pytest_unconfigure(config: pytest.Config) -> None:
    _monkeypatch.undo()
