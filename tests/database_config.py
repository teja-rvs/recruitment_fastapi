from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

PACKAGE_DIR = Path(__file__).resolve().parents[1] / "src" / "recruitment_fastapi"
TEST_ENV_FILE = PACKAGE_DIR / ".env.test"
APP_ENV_FILE = PACKAGE_DIR / ".env"

# Unit tests never connect; this only satisfies Settings at import time.
UNIT_DATABASE_URL = "postgresql+psycopg://unused:unused@127.0.0.1:1/pytest_unused"


def resolve_test_database_url(*, require_test_database: bool = False) -> str:
    if not TEST_ENV_FILE.is_file():
        if require_test_database:
            raise RuntimeError(
                f"Test database config not found: {TEST_ENV_FILE}. "
                "Set DATABASE_URL to the test database, not the app database."
            )
        return UNIT_DATABASE_URL

    database_url = dotenv_values(TEST_ENV_FILE).get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(f"{TEST_ENV_FILE} must set DATABASE_URL")

    app_database_url = dotenv_values(APP_ENV_FILE).get("DATABASE_URL")
    if app_database_url and _same_database(database_url, app_database_url):
        raise RuntimeError(
            "Tests must not use the application database. "
            f"{TEST_ENV_FILE} points at the same database as {APP_ENV_FILE}."
        )

    return database_url


def _same_database(left: str, right: str) -> bool:
    left_url = make_url(left)
    right_url = make_url(right)
    return (left_url.host, left_url.port, left_url.database) == (
        right_url.host,
        right_url.port,
        right_url.database,
    )
