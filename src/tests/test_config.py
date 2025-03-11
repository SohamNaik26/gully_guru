"""
Test configuration module.

This module provides configuration settings for tests to ensure they don't
affect the production environment.
"""

import os
from pathlib import Path

# Set test environment variables
os.environ["TEST_MODE"] = "true"
os.environ["ENVIRONMENT"] = "test"

# Use an in-memory SQLite database for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Use a test server URL for API tests
os.environ["API_BASE_URL"] = "http://testserver/api"

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"

# Create test data directory if it doesn't exist
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test database path (for file-based SQLite)
TEST_DB_PATH = TEST_DATA_DIR / "test.db"

# Test configuration
TEST_CONFIG = {
    "database_url": os.environ["DATABASE_URL"],
    "api_base_url": os.environ["API_BASE_URL"],
    "test_mode": True,
    "test_db_path": str(TEST_DB_PATH),
}
