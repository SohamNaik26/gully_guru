"""
Pytest configuration file for GullyGuru tests.

This file contains fixtures and configuration for pytest.
"""

import pytest
import asyncio
import logging

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# Set up pytest for asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Add more fixtures as needed for database setup, mocking, etc.
