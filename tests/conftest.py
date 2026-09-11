import pytest

from tests.database_config import resolve_test_database_url

_monkeypatch = pytest.MonkeyPatch()


def pytest_configure(config: pytest.Config) -> None:
    """Set DATABASE_URL before test modules import application Settings.

    Unit tests get a placeholder URL when ``.env.test`` is absent. Integration
    fixtures re-resolve it with ``require_test_database=True``.
    """
    _monkeypatch.setenv("DATABASE_URL", resolve_test_database_url())


def pytest_unconfigure(config: pytest.Config) -> None:
    _monkeypatch.undo()
