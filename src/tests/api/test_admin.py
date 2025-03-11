"""
Tests for Admin-related API endpoints
"""

from unittest.mock import MagicMock, AsyncMock

from src.tests.utils.mock_data import MockDataFactory


def test_get_gully_admins(test_client, mock_db):
    """Test retrieving all admins for a gully."""
    # Setup mock data
    gully_id = 1
    admin_participants = [
        MockDataFactory.mock_gully_participant(
            id=1, user_id=1, gully_id=gully_id, role="admin"
        ),
        MockDataFactory.mock_gully_participant(
            id=2, user_id=2, gully_id=gully_id, role="owner"
        ),
    ]

    admin_users = [
        MockDataFactory.mock_user(
            id=1, telegram_id=11111, username="admin1", full_name="Admin One"
        ),
        MockDataFactory.mock_user(
            id=2, telegram_id=22222, username="admin2", full_name="Admin Two"
        ),
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


def test_assign_admin_role(test_client, mock_db, mock_user):
    """Test assigning admin role to a user."""
    # Setup mock data
    gully_id = 1
    user_id = 2
    role_data = {"user_id": user_id, "gully_id": gully_id, "role": "admin"}

    # Mock the gully
    gully = MockDataFactory.mock_gully(id=gully_id)

    # Mock the user
    user = MockDataFactory.mock_user(id=user_id)

    # Mock the admin participant (current user)
    admin_participant = MockDataFactory.mock_gully_participant(
        user_id=mock_user.id, gully_id=gully_id, role="admin"
    )

    # Mock the target participant
    participant = MockDataFactory.mock_gully_participant(
        user_id=user_id, gully_id=gully_id, role="member"
    )

    # Configure mocks
    mock_db.get = AsyncMock(
        side_effect=lambda model, id: {gully_id: gully, user_id: user}.get(id)
    )

    # Mock execute for admin check
    admin_execute_result = MagicMock()
    admin_execute_result.scalars.return_value.first.return_value = admin_participant

    # Mock execute for participant check
    participant_execute_result = MagicMock()
    participant_execute_result.scalars.return_value.first.return_value = participant

    # Set up execute to return different results based on the query
    mock_db.execute = AsyncMock(
        side_effect=[admin_execute_result, participant_execute_result]
    )

    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    # Make request
    response = test_client.post(
        f"/api/admin/gully/{gully_id}/admins/{user_id}", json=role_data
    )

    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["gully_id"] == gully_id
    assert data["role"] == "admin"


def test_remove_admin_role(test_client, mock_db, mock_user):
    """Test removing admin role from a user."""
    # Setup mock data
    gully_id = 1
    user_id = 2

    # Mock the admin participant (current user)
    admin_participant = MockDataFactory.mock_gully_participant(
        user_id=mock_user.id, gully_id=gully_id, role="admin"
    )

    # Mock the target participant
    participant = MockDataFactory.mock_gully_participant(
        user_id=user_id, gully_id=gully_id, role="admin"
    )

    # Configure mocks
    # Mock execute for admin check
    admin_execute_result = MagicMock()
    admin_execute_result.scalars.return_value.first.return_value = admin_participant

    # Mock execute for participant check
    participant_execute_result = MagicMock()
    participant_execute_result.scalars.return_value.first.return_value = participant

    # Set up execute to return different results based on the query
    mock_db.execute = AsyncMock(
        side_effect=[admin_execute_result, participant_execute_result]
    )

    mock_db.commit = AsyncMock()

    # Make request
    response = test_client.delete(f"/api/admin/gully/{gully_id}/admins/{user_id}")

    # Verify response
    assert response.status_code == 204
