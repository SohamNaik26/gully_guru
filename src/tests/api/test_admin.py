"""
Tests for Admin-related API endpoints
"""

from unittest.mock import MagicMock, AsyncMock

from src.db.models import User, GullyParticipant


def test_get_gully_admins(test_client, mock_db):
    """Test retrieving all admins for a gully."""
    # Setup mock data
    gully_id = 1
    admin_participants = [
        GullyParticipant(id=1, user_id=1, gully_id=gully_id, role="admin"),
        GullyParticipant(id=2, user_id=2, gully_id=gully_id, role="owner"),
    ]

    admin_users = [
        User(id=1, telegram_id=11111, username="admin1", full_name="Admin One"),
        User(id=2, telegram_id=22222, username="admin2", full_name="Admin Two"),
    ]

    # Configure mocks
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = admin_participants
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Mock get method to return appropriate user
    mock_db.get = AsyncMock(
        side_effect=lambda model, id: admin_users[0] if id == 1 else admin_users[1]
    )

    # Make request
    response = test_client.get(f"/api/admin/gully/{gully_id}/admins")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "admin1"
    assert data[0]["role"] == "admin"
    assert data[1]["username"] == "admin2"
    assert data[1]["role"] == "owner"


def test_get_gully_admins_no_admins(test_client, mock_db):
    """Test retrieving admins for a gully with no admins."""
    # Setup mock data
    gully_id = 1

    # Configure mocks
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get(f"/api/admin/gully/{gully_id}/admins")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_gully_admins_user_not_found(test_client, mock_db):
    """Test retrieving admins when a user is not found."""
    # Setup mock data
    gully_id = 1
    admin_participants = [
        GullyParticipant(id=1, user_id=1, gully_id=gully_id, role="admin"),
    ]

    # Configure mocks
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = admin_participants
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Mock get method to return None (user not found)
    mock_db.get = AsyncMock(return_value=None)

    # Make request
    response = test_client.get(f"/api/admin/gully/{gully_id}/admins")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
