"""
Tests for User-related API endpoints
"""

from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from src.tests.utils.mock_data import MockDataFactory


def test_get_all_users(test_client, mock_db):
    """Test retrieving all users."""
    # Setup mock data
    users_data = [
        MockDataFactory.user(id=1, username="user1"),
        MockDataFactory.user(id=2, username="user2"),
    ]

    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = users_data
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get("/api/users")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user1"
    assert data[1]["username"] == "user2"


def test_get_users_with_telegram_id_filter(test_client, mock_db):
    """Test retrieving users filtered by telegram_id."""
    # Setup mock data
    telegram_id = 12345678
    user = MockDataFactory.user(id=1, telegram_id=telegram_id)

    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = [user]
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get(f"/api/users?telegram_id={telegram_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["telegram_id"] == telegram_id


def test_get_user_by_id(test_client, mock_db):
    """Test retrieving a user by ID."""
    # Setup mock data
    user_id = 1
    user = MockDataFactory.user(id=user_id, username="testuser")

    # Configure mock
    mock_db.get = AsyncMock(return_value=user)

    # Make request
    response = test_client.get(f"/api/users/{user_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "testuser"


def test_get_user_by_id_not_found(test_client, mock_db):
    """Test retrieving a non-existent user."""
    # Configure mock
    mock_db.get = AsyncMock(return_value=None)

    # Make request
    response = test_client.get("/api/users/999")

    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_user_by_telegram_id(test_client, mock_db):
    """Test retrieving a user by telegram ID."""
    # Setup mock data
    telegram_id = 12345678
    user = MockDataFactory.user(id=1, telegram_id=telegram_id)

    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = user
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get(f"/api/users/telegram/{telegram_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == telegram_id


def test_get_user_by_telegram_id_not_found(test_client, mock_db):
    """Test retrieving a non-existent user by telegram ID."""
    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = None
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get("/api/users/telegram/999999")

    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_create_user(test_client, mock_db):
    """Test creating a new user."""
    # Setup mock data
    user_data = {
        "telegram_id": 12345678,
        "username": "newuser",
        "full_name": "New User",
    }

    # Configure mock to indicate user doesn't exist
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = None
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Mock the refresh method
    async def mock_refresh(obj):
        obj.id = 1
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)
        return obj

    mock_db.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    # Make request
    response = test_client.post("/api/users/", json=user_data)

    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["telegram_id"] == user_data["telegram_id"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]


def test_create_user_conflict(test_client, mock_db):
    """Test creating a user that already exists."""
    # Setup mock data
    existing_user = MockDataFactory.user(id=1, telegram_id=12345678)
    user_data = {
        "telegram_id": 12345678,
        "username": "newuser",
        "full_name": "New User",
    }

    # Configure mock to indicate user already exists
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = existing_user
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.post("/api/users/", json=user_data)

    # Verify response
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
