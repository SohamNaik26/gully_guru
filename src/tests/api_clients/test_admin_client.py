"""
Tests for the AdminService client.
"""

import pytest
import pytest_asyncio

from src.api.services.admin.client import AdminService
from src.tests.api_clients.mocks.data_factory import MockDataFactory


@pytest_asyncio.fixture
async def admin_service(mock_httpx_client, base_url):
    """Create an AdminService instance for testing."""
    return AdminService(base_url, client=mock_httpx_client)


class TestAdminService:
    """Tests for the AdminService client."""

    @pytest.mark.asyncio
    async def test_get_user_permissions(
        self, admin_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting user permissions for a gully."""
        # Setup test data
        user_id = 42
        gully_id = 123
        mock_permissions = [
            MockDataFactory.permission(name="read"),
            MockDataFactory.permission(name="write"),
        ]

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=200, json_data=mock_permissions
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await admin_service.get_user_permissions(user_id, gully_id)

        # Assertions
        assert len(result) == 2
        assert result[0]["name"] == "read"
        assert result[1]["name"] == "write"
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_permissions_error(
        self, admin_service, mock_httpx_client, mock_response_factory
    ):
        """Test error handling when getting user permissions."""
        # Configure mock response for error
        mock_response = mock_response_factory(
            status_code=404, json_data={"error": "User or gully not found"}
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await admin_service.get_user_permissions(999, 999)

        # Assertions
        assert result == []
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gully_admins(
        self, admin_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting all admins of a gully."""
        # Setup test data
        gully_id = 123
        mock_admins = [MockDataFactory.user(id=1), MockDataFactory.user(id=2)]

        # Configure mock response
        mock_response = mock_response_factory(status_code=200, json_data=mock_admins)
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await admin_service.get_gully_admins(gully_id)

        # Assertions
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gully_admins_error(
        self, admin_service, mock_httpx_client, mock_response_factory
    ):
        """Test error handling when getting gully admins."""
        # Configure mock response for error
        mock_response = mock_response_factory(
            status_code=404, json_data={"error": "Gully not found"}
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await admin_service.get_gully_admins(999)

        # Assertions
        assert result == []
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_network_error_handling(self, admin_service, mock_httpx_client):
        """Test handling of network errors."""
        # Configure mock to raise an exception
        mock_httpx_client.get.side_effect = Exception("Network error")

        # Call the method
        result = await admin_service.get_user_permissions(1, 2)

        # Assertions
        assert result == []
        mock_httpx_client.get.assert_called_once()
