import pytest

from app.core.config import AppConfig


@pytest.fixture
def app_config() -> AppConfig:
    """Fixture for AppConfig."""
    return AppConfig.from_env()
