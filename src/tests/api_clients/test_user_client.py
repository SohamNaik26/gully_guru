"""
Tests for the UserService client.
"""

import pytest
import pytest_asyncio

from src.api.services.users.client import UserService
from src.tests.api_clients.mocks.data_factory import MockDataFactory


@pytest_asyncio.fixture
async def user_service(mock_httpx_client, base_url):
    """Create a UserService instance for testing."""
    return UserService(base_url, client=mock_httpx_client)


class TestUserService:
    """Tests for the UserService client."""

    @pytest.mark.asyncio
    async def test_get_user(
        self, user_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a user by Telegram ID."""
        # Setup test data
        telegram_id = 123456
        mock_user = MockDataFactory.user(telegram_id=telegram_id)

        # Configure mock response
        mock_response = mock_response_factory(status_code=200, json_data=mock_user)
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await user_service.get_user(telegram_id)

        # Assertions
        assert result is not None
        assert result["telegram_id"] == telegram_id
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_not_found(
        self, user_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a non-existent user."""
        # Configure mock response for not found
        mock_response = mock_response_factory(
            status_code=404, json_data={"error": "User not found"}
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await user_service.get_user(999999)

        # Assertions
        assert result is None
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user(
        self, user_service, mock_httpx_client, mock_response_factory
    ):
        """Test creating a new user."""
        # Setup test data
        user_data = {
            "telegram_id": 123456,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
        }
        mock_created_user = MockDataFactory.user(**user_data)

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=201, json_data=mock_created_user
        )
        mock_httpx_client.post.return_value = mock_response

        # Call the method
        result = await user_service.create_user(user_data)

        # Assertions
        assert result is not None
        assert result["telegram_id"] == user_data["telegram_id"]
        assert result["first_name"] == user_data["first_name"]
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_error(
        self, user_service, mock_httpx_client, mock_response_factory
    ):
        """Test error handling when creating a user."""
        # Configure mock response for error
        mock_response = mock_response_factory(
            status_code=400, json_data={"error": "Invalid user data"}
        )
        mock_httpx_client.post.return_value = mock_response

        # Call the method
        result = await user_service.create_user({"invalid": "data"})

        # Assertions
        assert result is None
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user(
        self, user_service, mock_httpx_client, mock_response_factory
    ):
        """Test updating a user."""
        # Setup test data
        telegram_id = 123456
        update_data = {"first_name": "Updated"}
        mock_updated_user = MockDataFactory.user(
            telegram_id=telegram_id, first_name="Updated"
        )

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=200, json_data=mock_updated_user
        )
        mock_httpx_client.put.return_value = mock_response

        # Call the method
        result = await user_service.update_user(telegram_id, update_data)

        # Assertions
        assert result is not None
        assert result["telegram_id"] == telegram_id
        assert result["first_name"] == "Updated"
        mock_httpx_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user(
        self, user_service, mock_httpx_client, mock_response_factory
    ):
        """Test deleting a user."""
        # Configure mock response
        mock_response = mock_response_factory(
            status_code=200, json_data={"success": True}
        )
        mock_httpx_client.delete.return_value = mock_response

        # Call the method
        result = await user_service.delete_user(123456)

        # Assertions
        assert result is True
        mock_httpx_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self, user_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a user by database ID."""
        # Setup test data
        user_id = 42
        mock_user = MockDataFactory.user(id=user_id)

        # Configure mock response
        mock_response = mock_response_factory(status_code=200, json_data=mock_user)
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await user_service.get_user_by_id(user_id)

        # Assertions
        assert result is not None
        assert result["id"] == user_id
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_network_error_handling(self, user_service, mock_httpx_client):
        """Test handling of network errors."""
        # Configure mock to raise an exception
        mock_httpx_client.get.side_effect = Exception("Network error")

        # Call the method
        result = await user_service.get_user(123456)

        # Assertions
        assert result is None
        mock_httpx_client.get.assert_called_once()
