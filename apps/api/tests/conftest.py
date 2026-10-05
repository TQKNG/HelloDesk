from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient

from app.core.settings import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(guest_session_ttl_seconds=900, pending_action_ttl_seconds=120)


@pytest.fixture
def client(settings: Settings) -> TestClient:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
