"""
Tests for the API client factory.
"""

import pytest
import pytest_asyncio

from src.api.client import APIClient


@pytest_asyncio.fixture
async def api_client(base_url):
    """Create an APIClient instance for testing."""
    client = APIClient(base_url)
    yield client
    await client.close()


class TestAPIClient:
    """Tests for the APIClient factory."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, api_client):
        """Test that the client is properly initialized with all services."""
        assert api_client.users is not None
        assert api_client.admin is not None
        assert api_client.gullies is not None

    @pytest.mark.asyncio
    async def test_client_context_manager(self, base_url):
        """Test that the client works as a context manager."""
        async with APIClient(base_url) as client:
            assert client.users is not None
            assert client.admin is not None
            assert client.gullies is not None

    @pytest.mark.asyncio
    async def test_client_close(self, base_url):
        """Test that the client can be closed properly."""
        client = APIClient(base_url)
        await client.close()
        # No assertion needed, just checking that it doesn't raise an exception
