import pytest
from fastapi.testclient import TestClient

from recruitment_fastapi.main import app


@pytest.fixture
def client():
    return TestClient(app)
