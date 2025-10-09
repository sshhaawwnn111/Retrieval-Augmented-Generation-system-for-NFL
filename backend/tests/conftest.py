"""
Test configuration
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from app.core.config import settings
    return settings
