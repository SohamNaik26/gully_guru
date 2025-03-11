"""
Isolated tests for User-related API endpoints that don't rely on the actual application
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from src.api.routes.users import router as user_router
from src.tests.utils.mock_models import MockUser
from src.tests.utils.mock_data import MockDataFactory


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def isolated_app(mock_db):
    """Create an isolated FastAPI app with mocked dependencies."""
    app = FastAPI()

    # Override the get_session dependency
    async def get_mock_db():
        yield mock_db

    # Add the user router with the overridden dependency
    from src.db.session import get_session

    app.dependency_overrides[get_session] = get_mock_db
    app.include_router(user_router, prefix="/api/users")

    return app


@pytest.fixture
def test_client(isolated_app):
    """Create a test client for the isolated app."""
    return TestClient(isolated_app)


def test_get_all_users(test_client, mock_db):
    """Test retrieving all users."""
    # Setup mock data
    users_data = [
        MockDataFactory.mock_user(id=1, username="user1"),
        MockDataFactory.mock_user(id=2, username="user2"),
    ]

    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = users_data
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get("/api/users/")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user1"
    assert data[1]["username"] == "user2"


def test_get_users_with_telegram_id_filter(test_client, mock_db):
    """Test retrieving users with telegram_id filter."""
    # Setup mock data
    telegram_id = 12345
    users_data = [MockDataFactory.mock_user(id=1, telegram_id=telegram_id)]

    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = users_data
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get(f"/api/users/?telegram_id={telegram_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["telegram_id"] == telegram_id


def test_get_user_by_id(test_client, mock_db):
    """Test retrieving a user by ID."""
    # Setup mock data
    user_id = 1
    user = MockDataFactory.mock_user(id=user_id)

    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = user
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get(f"/api/users/{user_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id


def test_get_user_by_id_not_found(test_client, mock_db):
    """Test retrieving a non-existent user by ID."""
    # Configure mock
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = None
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make request
    response = test_client.get("/api/users/999")

    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_user_by_telegram_id(test_client, mock_db):
    """Test retrieving a user by telegram ID."""
    # Setup mock data
    telegram_id = 12345
    user = MockDataFactory.mock_user(telegram_id=telegram_id)

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
    response = test_client.get("/api/users/telegram/999")

    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch("src.api.routes.users.create_user")
def test_create_user(mock_create_user, test_client):
    """Test creating a new user."""
    # Setup mock data
    user_data = {
        "telegram_id": 12345678,
        "username": "new_user",
        "full_name": "New User",
    }

    # Create a mock user to return
    mock_user = MockUser(
        id=1,
        telegram_id=user_data["telegram_id"],
        username=user_data["username"],
        full_name=user_data["full_name"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Configure the mock to return our mock user
    async def mock_create_user_impl(*args, **kwargs):
        return mock_user

    mock_create_user.side_effect = mock_create_user_impl

    # Make request
    response = test_client.post("/api/users/", json=user_data)

    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["telegram_id"] == user_data["telegram_id"]
    assert data["full_name"] == user_data["full_name"]


@patch("src.api.routes.users.create_user")
def test_create_user_conflict(mock_create_user, test_client):
    """Test creating a user with an existing telegram_id."""
    # Setup mock data
    telegram_id = 12345678
    user_data = {
        "telegram_id": telegram_id,
        "username": "new_user",
        "full_name": "New User",
    }

    # Configure the mock to raise a conflict exception
    async def mock_create_user_impl(*args, **kwargs):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_id {telegram_id} already exists",
        )

    mock_create_user.side_effect = mock_create_user_impl

    # Make request
    response = test_client.post("/api/users/", json=user_data)

    # Verify response
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data["detail"].lower()
