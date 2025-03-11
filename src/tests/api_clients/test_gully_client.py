"""
Tests for the GullyService client.
"""

import pytest
import pytest_asyncio

from src.api.services.gullies.client import GullyService
from src.tests.api_clients.mocks.data_factory import MockDataFactory


@pytest_asyncio.fixture
async def gully_service(mock_httpx_client, base_url):
    """Create a GullyService instance for testing."""
    return GullyService(base_url, client=mock_httpx_client)


class TestGullyService:
    """Tests for the GullyService client."""

    @pytest.mark.asyncio
    async def test_get_all_gullies(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting all gullies."""
        # Setup test data
        mock_gullies = [
            MockDataFactory.gully(id=1, name="Gully 1"),
            MockDataFactory.gully(id=2, name="Gully 2"),
        ]

        # Configure mock response
        mock_response = mock_response_factory(status_code=200, json_data=mock_gullies)
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_all_gullies()

        # Assertions
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Gully 1"
        assert result[1]["id"] == 2
        assert result[1]["name"] == "Gully 2"
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gully(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a gully by ID."""
        # Setup test data
        gully_id = 42
        mock_gully = MockDataFactory.gully(id=gully_id, name="Test Gully")

        # Configure mock response
        mock_response = mock_response_factory(status_code=200, json_data=mock_gully)
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_gully(gully_id)

        # Assertions
        assert result is not None
        assert result["id"] == gully_id
        assert result["name"] == "Test Gully"
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gully_not_found(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a non-existent gully."""
        # Configure mock response for not found
        mock_response = mock_response_factory(
            status_code=404, json_data={"error": "Gully not found"}
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_gully(999)

        # Assertions
        assert result is None
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gully_by_group(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a gully by telegram group ID."""
        # Setup test data
        group_id = 123456
        mock_gully = MockDataFactory.gully(
            telegram_group_id=group_id, name="Test Group"
        )

        # Configure mock response
        mock_response = mock_response_factory(status_code=200, json_data=mock_gully)
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_gully_by_group(group_id)

        # Assertions
        assert result is not None
        assert result["telegram_group_id"] == group_id
        assert result["name"] == "Test Group"
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_gully(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test creating a new gully."""
        # Setup test data
        gully_data = {"name": "New Gully", "telegram_group_id": 123456}
        mock_created_gully = MockDataFactory.gully(**gully_data)

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=201, json_data=mock_created_gully
        )
        mock_httpx_client.post.return_value = mock_response

        # Call the method
        result = await gully_service.create_gully(
            name=gully_data["name"], telegram_group_id=gully_data["telegram_group_id"]
        )

        # Assertions
        assert result is not None
        assert result["name"] == gully_data["name"]
        assert result["telegram_group_id"] == gully_data["telegram_group_id"]
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gully_participants(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting participants of a gully."""
        # Setup test data
        gully_id = 42
        mock_participants = [
            MockDataFactory.gully_participant(gully_id=gully_id, user_id=1),
            MockDataFactory.gully_participant(gully_id=gully_id, user_id=2),
        ]

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=200, json_data=mock_participants
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_gully_participants(gully_id)

        # Assertions
        assert len(result) == 2
        assert result[0]["gully_id"] == gully_id
        assert result[0]["user_id"] == 1
        assert result[1]["gully_id"] == gully_id
        assert result[1]["user_id"] == 2
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_gully_participations(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting all gully participations for a user."""
        # Setup test data
        user_id = 42
        mock_participations = [
            MockDataFactory.gully_participant(user_id=user_id, gully_id=1),
            MockDataFactory.gully_participant(user_id=user_id, gully_id=2),
        ]

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=200, json_data=mock_participations
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_user_gully_participations(user_id)

        # Assertions
        assert len(result) == 2
        assert result[0]["user_id"] == user_id
        assert result[0]["gully_id"] == 1
        assert result[1]["user_id"] == user_id
        assert result[1]["gully_id"] == 2
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_gully_participation(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a specific participation for a user in a gully."""
        # Setup test data
        user_id = 42
        gully_id = 123
        mock_participation = [
            MockDataFactory.gully_participant(user_id=user_id, gully_id=gully_id)
        ]

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=200, json_data=mock_participation
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_user_gully_participation(user_id, gully_id)

        # Assertions
        assert result is not None
        assert result["user_id"] == user_id
        assert result["gully_id"] == gully_id
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_user_to_gully(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test adding a user to a gully."""
        # Setup test data
        user_id = 42
        gully_id = 123
        role = "admin"
        mock_participation = MockDataFactory.gully_participant(
            user_id=user_id, gully_id=gully_id, role=role
        )

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=201, json_data=mock_participation
        )
        mock_httpx_client.post.return_value = mock_response

        # Call the method
        result = await gully_service.add_user_to_gully(user_id, gully_id, role)

        # Assertions
        assert result is not None
        assert result["user_id"] == user_id
        assert result["gully_id"] == gully_id
        assert result["role"] == role
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_gully_participant_role(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test updating a participant's role."""
        # Setup test data
        participant_id = 42
        new_role = "admin"
        mock_updated = MockDataFactory.gully_participant(
            id=participant_id, role=new_role
        )

        # Configure mock response
        mock_response = mock_response_factory(status_code=200, json_data=mock_updated)
        mock_httpx_client.put.return_value = mock_response

        # Call the method
        result = await gully_service.update_gully_participant_role(
            participant_id, new_role
        )

        # Assertions
        assert result is not None
        assert result["id"] == participant_id
        assert result["role"] == new_role
        mock_httpx_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_gully_participant(
        self, gully_service, mock_httpx_client, mock_response_factory
    ):
        """Test getting a participant by ID."""
        # Setup test data
        participant_id = 42
        mock_participant = MockDataFactory.gully_participant(id=participant_id)

        # Configure mock response
        mock_response = mock_response_factory(
            status_code=200, json_data=mock_participant
        )
        mock_httpx_client.get.return_value = mock_response

        # Call the method
        result = await gully_service.get_gully_participant(participant_id)

        # Assertions
        assert result is not None
        assert result["id"] == participant_id
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_network_error_handling(self, gully_service, mock_httpx_client):
        """Test handling of network errors."""
        # Configure mock to raise an exception
        mock_httpx_client.get.side_effect = Exception("Network error")

        # Call the method
        result = await gully_service.get_all_gullies()

        # Assertions
        assert result == []
        mock_httpx_client.get.assert_called_once()
