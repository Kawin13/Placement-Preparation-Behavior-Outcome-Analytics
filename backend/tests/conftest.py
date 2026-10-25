"""
Pytest configuration for isolated test database execution.
Guarantees that automated test suites execute against 'placement_portal_test',
never mutating or altering the local development database ('placement_portal').
"""

import os

# Point to dedicated test database BEFORE any app modules are imported
TEST_DB_URL = "postgresql://postgres:postgres@localhost:5432/placement_portal_test"
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["ENVIRONMENT"] = "development"

import pytest
from app.core.config import settings
settings.DATABASE_URL = TEST_DB_URL
settings.ENVIRONMENT = "development"

from app.core.database import SessionLocal, engine
from app.core.rate_limit import login_rate_limiter, register_rate_limiter, reset_rate_limiter


@pytest.fixture(autouse=True)
def reset_global_rate_limiters():
    """Reset IP-based rate limiters to prevent cross-test interference."""
    login_rate_limiter.reset_for_test()
    register_rate_limiter.reset_for_test()
    reset_rate_limiter.reset_for_test()
    yield
