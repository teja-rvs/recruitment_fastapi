from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_ENV_FILE = PROJECT_ROOT / ".env.test"


def load_test_environment():
    load_dotenv(
        TEST_ENV_FILE,
        override=True,
    )
