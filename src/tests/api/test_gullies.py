"""
Tests for Gully-related API endpoints
"""

from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from src.tests.utils.mock_data import MockDataFactory
from src.tests.utils.mock_deps import MockDBUtil
from src.db.models import Gully, GullyParticipant, User


def test_get_all_gullies(test_client, mock_db, mock_response_factory):
    """Test retrieving all gullies."""
    # Setup mock data
    gullies_data = [
        MockDataFactory.gully(id=1, name="Gully 1"),
        MockDataFactory.gully(id=2, name="Gully 2"),
    ]

    # Configure mock
    MockDBUtil.configure_execute(mock_db, gullies_data)

    # Make request
    response = test_client.get("/api/gullies/")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Gully 1"
    assert data[1]["name"] == "Gully 2"
    assert "created_at" in data[0]
    assert "updated_at" in data[0]


def test_get_gully_by_id(test_client, mock_db):
    """Test retrieving a gully by ID."""
    # Setup mock data
    gully_data = MockDataFactory.gully(id=1, name="Test Gully")

    # Configure mock
    MockDBUtil.configure_get(mock_db, Gully, gully_data)

    # Make request
    response = test_client.get("/api/gullies/1")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Gully"
    assert "telegram_group_id" in data


def test_get_gully_by_id_not_found(test_client, mock_db):
    """Test retrieving a non-existent gully by ID."""
    # Configure mock to return None
    MockDBUtil.configure_get(mock_db, Gully, None)

    # Make request
    response = test_client.get("/api/gullies/999")

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_gully_by_chat_id(test_client, mock_db):
    """Test retrieving a gully by telegram group ID."""
    # Setup mock data
    telegram_group_id = 87654321
    gully_data = MockDataFactory.gully(id=1, telegram_group_id=telegram_group_id)

    # Configure mock
    MockDBUtil.configure_execute(mock_db, gully_data, scalar_first=True)

    # Make request
    response = test_client.get(f"/api/gullies/group/{telegram_group_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["telegram_group_id"] == telegram_group_id


def test_get_gully_by_chat_id_not_found(test_client, mock_db):
    """Test retrieving a non-existent gully by telegram group ID."""
    # Configure mock to return None
    MockDBUtil.configure_execute(mock_db, None, scalar_first=True)

    # Make request
    response = test_client.get("/api/gullies/group/999999")

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_gully(test_client, mock_db, mock_user):
    """Test creating a new gully."""
    # Configure mocks
    MockDBUtil.configure_execute(
        mock_db, None, scalar_first=True
    )  # No existing gully with same telegram_group_id
    MockDBUtil.configure_commit(mock_db)

    # Mock the refresh method to set the ID and other required fields
    async def mock_refresh(obj):
        if isinstance(obj, Gully):
            obj.id = 1
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)
        return obj

    mock_db.refresh = AsyncMock(side_effect=mock_refresh)
    MockDBUtil.configure_add(mock_db)  # Configure add method

    # Make request
    response = test_client.post(
        "/api/gullies/",
        json={
            "name": "Test Gully",
            "telegram_group_id": 12345678,
            "start_date": "2025-04-01T00:00:00Z",
            "end_date": "2025-05-31T00:00:00Z",
        },
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Gully"
    assert data["telegram_group_id"] == 12345678
    assert data["status"] == "pending"


def test_create_gully_conflict(test_client, mock_db):
    """Test creating a gully with an existing telegram_group_id."""
    # Setup mock data
    existing_gully = MockDataFactory.gully(id=1, telegram_group_id=12345678)
    gully_data = {"name": "New Gully", "telegram_group_id": 12345678}

    # Configure mock to return an existing gully
    MockDBUtil.configure_execute(mock_db, existing_gully, scalar_first=True)

    # Make request
    response = test_client.post("/api/gullies/", json=gully_data)

    # Verify response
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data


def test_get_participants(test_client, mock_db, mock_user):
    """Test retrieving participants with no filters."""
    # Setup mock data
    participants_data = [
        MockDataFactory.gully_participant(id=1, user_id=1, gully_id=1),
        MockDataFactory.gully_participant(id=2, user_id=2, gully_id=1),
    ]

    # Configure mock
    MockDBUtil.configure_execute(mock_db, participants_data)

    # Make request
    response = test_client.get("/api/participants")

    # Print response body for debugging
    print("Response body:", response.json())

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2


def test_get_participants_filter_by_gully(test_client, mock_db, mock_user):
    """Test retrieving participants filtered by gully_id."""
    # Setup mock data for gully existence check
    gully_data = MockDataFactory.gully(id=1)
    # Setup mock data for participants
    participants_data = [
        MockDataFactory.gully_participant(id=1, user_id=1, gully_id=1),
        MockDataFactory.gully_participant(id=2, user_id=2, gully_id=1),
    ]

    # Configure mocks
    MockDBUtil.configure_get(mock_db, Gully, gully_data)
    MockDBUtil.configure_execute(mock_db, participants_data)

    # Make request
    response = test_client.get("/api/participants?gully_id=1")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["gully_id"] == 1
    assert data[1]["gully_id"] == 1


def test_get_participants_filter_by_gully_not_found(test_client, mock_db):
    """Test retrieving participants for a non-existent gully."""
    # Configure mock to return None for gully existence check
    MockDBUtil.configure_get(mock_db, Gully, None)

    # Make request
    response = test_client.get("/api/participants?gully_id=999")

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_get_participants_filter_by_user(test_client, mock_db, mock_user):
    """Test retrieving participants filtered by user_id."""
    # Setup mock data for user existence check
    user_data = MockDataFactory.user(id=1)
    # Setup mock data for participants
    participants_data = [
        MockDataFactory.gully_participant(id=1, user_id=1, gully_id=1),
        MockDataFactory.gully_participant(id=3, user_id=1, gully_id=2),
    ]

    # Configure mocks
    MockDBUtil.configure_get(mock_db, User, user_data)
    MockDBUtil.configure_execute(mock_db, participants_data)

    # Mock is_system_admin to return True
    with patch("src.api.routes.gullies.is_system_admin", AsyncMock(return_value=True)):
        # Make request
        response = test_client.get("/api/participants?user_id=1")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["user_id"] == 1
        assert data[1]["user_id"] == 1


def test_get_participant_by_id(test_client, mock_db, mock_user):
    """Test retrieving a specific participant by ID."""
    # Setup mock data
    participant_data = MockDataFactory.gully_participant(id=1, user_id=1, gully_id=1)

    # Configure mock
    MockDBUtil.configure_get(mock_db, GullyParticipant, participant_data)

    # Make request
    response = test_client.get("/api/participants/1")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["user_id"] == 1
    assert data["gully_id"] == 1


def test_get_participant_by_id_not_found(test_client, mock_db):
    """Test retrieving a non-existent participant by ID."""
    # Configure mock
    MockDBUtil.configure_get(mock_db, GullyParticipant, None)

    # Make request
    response = test_client.get("/api/participants/999")

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_add_participant(test_client, mock_db, mock_user):
    """Test adding a participant to a gully."""
    # Setup mock data
    gully_id = 1
    user_id = 2
    team_name = "Test Team"
    role = "member"

    # Configure mocks
    MockDBUtil.configure_get(mock_db, Gully, MockDataFactory.gully(id=gully_id))
    MockDBUtil.configure_get(mock_db, User, MockDataFactory.user(id=user_id))
    MockDBUtil.configure_execute(
        mock_db, None, scalar_first=True
    )  # No existing participant

    # Mock the is_gully_admin function to return True
    with patch("src.api.routes.gullies.is_gully_admin", return_value=True):
        # Mock the session.add and session.refresh methods
        async def mock_refresh(obj):
            # Set the ID and timestamps
            obj.id = 1
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)

        mock_db.refresh.side_effect = mock_refresh

        # Make request
        response = test_client.post(
            f"/api/gullies/{gully_id}/participants/",
            json={"user_id": user_id, "team_name": team_name},
            params={"role": role},
        )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["gully_id"] == gully_id
    assert data["team_name"] == team_name
    assert data["role"] == role
    assert "budget" in data
    assert "points" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_add_participant_gully_not_found(test_client, mock_db):
    """Test adding a participant to a non-existent gully."""
    # Configure mock to return None for gully existence check
    MockDBUtil.configure_get(mock_db, Gully, None)

    # Make request
    response = test_client.post(
        "/api/participants?gully_id=999&role=member",
        json={"user_id": 1, "team_name": "Test Team"},
    )

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_add_participant_user_not_found(test_client, mock_db):
    """Test adding a non-existent user to a gully."""
    # Configure mocks
    MockDBUtil.configure_get(
        mock_db, Gully, MockDataFactory.gully(id=1)
    )  # Gully exists
    MockDBUtil.configure_get(mock_db, User, None)  # User doesn't exist

    # Make request
    response = test_client.post(
        "/api/participants?gully_id=1&role=member",
        json={"user_id": 999, "team_name": "Test Team"},
    )

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_add_participant_already_exists(test_client, mock_db):
    """Test adding a user who is already in the gully."""
    # Configure mocks
    gully_id = 1
    user_id = 1

    # Create mock objects
    gully = Gully(id=gully_id, name="Test Gully", telegram_group_id=123)
    user = User(id=user_id, username="testuser")
    existing_participant = GullyParticipant(
        id=1,
        user_id=user_id,
        gully_id=gully_id,
        team_name="Existing Team",
        role="member",
        is_active=True,
        registration_complete=True,
    )

    # Configure mocks
    mock_db.get = AsyncMock(
        side_effect=lambda model, id: gully if model == Gully else user
    )

    # Create a MagicMock for the result of execute
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = existing_participant
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make session.add a regular MagicMock to avoid coroutine warnings
    mock_db.add = MagicMock()

    # Make the request
    response = test_client.post(
        f"/api/participants?gully_id={gully_id}&role=member",
        json={"user_id": user_id, "team_name": "Test Team"},
    )

    # Assert response
    assert response.status_code == 409
    assert response.json()["detail"] == f"User {user_id} is already in gully {gully_id}"


def test_update_participant_status_activate(test_client, mock_db, mock_user):
    """Test activating a participant."""
    # Setup mock data
    participant_id = 1
    participant = GullyParticipant(
        id=participant_id,
        user_id=mock_user.id,
        gully_id=1,
        team_name="Test Team",
        role="member",
        is_active=False,
        registration_complete=False,
        budget=100.0,
        points=0,
    )

    # Configure mocks
    mock_db.get = AsyncMock(return_value=participant)

    # Create a MagicMock for the result of execute
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=execute_result)

    # Make session.add a regular MagicMock to avoid coroutine warnings
    mock_db.add = MagicMock()

    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    # Mock is_gully_admin to return an awaitable that resolves to True
    with patch("src.api.routes.gullies.is_gully_admin", AsyncMock(return_value=True)):
        # Make the request
        response = test_client.put(
            f"/api/participants/{participant_id}",
            json={"action": "activate"},
        )

    # Assert response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == participant_id
    assert response_data["is_active"] is True


def test_update_participant_status_complete_registration(
    test_client, mock_db, mock_user
):
    """Test completing registration for a participant."""
    # Setup mock data
    participant_data = MockDataFactory.gully_participant(
        id=1, user_id=1, gully_id=1, registration_complete=False
    )

    # Configure mocks
    MockDBUtil.configure_get(mock_db, GullyParticipant, participant_data)
    MockDBUtil.configure_commit(mock_db)
    MockDBUtil.configure_refresh(mock_db)
    MockDBUtil.configure_add(mock_db)  # Configure add method

    # Mock the is_gully_admin function
    with patch("src.api.routes.gullies.is_gully_admin", AsyncMock(return_value=True)):
        # Make request
        response = test_client.put(
            "/api/participants/1",
            json={"action": "complete_registration"},
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["registration_complete"] is True


def test_update_participant_status_not_found(test_client, mock_db):
    """Test updating status for a non-existent participant."""
    # Configure mock
    MockDBUtil.configure_get(mock_db, GullyParticipant, None)

    # Make request
    response = test_client.put(
        "/api/participants/999",
        json={"action": "activate"},
    )

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_update_participant_status_invalid_action(test_client, mock_db, mock_user):
    """Test updating a participant with an invalid action."""
    # Setup mock data
    participant_id = 1
    participant = GullyParticipant(
        id=participant_id,
        user_id=mock_user.id,
        gully_id=1,
        team_name="Test Team",
        role="member",
        is_active=True,
        registration_complete=True,
    )

    # Configure mocks
    mock_db.get = AsyncMock(return_value=participant)

    # Mock is_gully_admin to return an awaitable that resolves to True
    async def mock_is_gully_admin(*args, **kwargs):
        return True

    with patch("src.api.routes.gullies.is_gully_admin", mock_is_gully_admin):
        # Make the request
        response = test_client.put(
            f"/api/participants/{participant_id}",
            json={"action": "invalid_action"},
        )

    # Assert response
    assert response.status_code == 400
    assert "Invalid action" in response.json()["detail"]


def test_update_participant_role(test_client, mock_db, mock_user):
    """Test updating a participant's role."""
    # Setup mock data
    participant_id = 1
    new_role = "admin"

    # Create a mock participant
    participant = GullyParticipant(
        id=participant_id,
        user_id=2,  # Different from mock_user.id
        gully_id=1,
        team_name="Test Team",
        budget=100.0,
        points=0,
        role="member",
    )

    # Configure mocks
    MockDBUtil.configure_get(mock_db, GullyParticipant, participant)

    # Mock the is_gully_admin function to return True
    with patch("src.api.routes.gullies.is_gully_admin", return_value=True):
        # Make request
        response = test_client.put(
            f"/api/gullies/participants/{participant_id}",
            json={"role": new_role},
        )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == new_role
    assert data["user_id"] == participant.user_id
    assert data["gully_id"] == participant.gully_id
    assert data["team_name"] == participant.team_name


def test_update_participant_role_not_found(test_client, mock_db):
    """Test updating role for a non-existent participant."""
    # Configure mock
    MockDBUtil.configure_get(mock_db, GullyParticipant, None)

    # Make request
    response = test_client.put(
        "/api/participants/999",
        json={"role": "admin"},
    )

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_update_participant_role_invalid_role(test_client, mock_db, mock_user):
    """Test updating a participant with an invalid role."""
    # Setup mock data
    participant_id = 1
    participant = GullyParticipant(
        id=participant_id,
        user_id=2,  # Different from mock_user.id
        gully_id=1,
        team_name="Test Team",
        role="member",
        is_active=True,
        registration_complete=True,
    )

    # Configure mocks
    mock_db.get = AsyncMock(return_value=participant)

    # Mock is_gully_admin to return an awaitable that resolves to True
    async def mock_is_gully_admin(*args, **kwargs):
        return True

    with patch("src.api.routes.gullies.is_gully_admin", mock_is_gully_admin):
        # Make the request
        response = test_client.put(
            f"/api/participants/{participant_id}",
            json={"role": "invalid_role"},
        )

    # Assert response
    assert response.status_code == 400
    assert "Invalid role" in response.json()["detail"]


def test_update_participant_role_not_admin(test_client, mock_db, mock_user):
    """Test updating role when not an admin."""
    # Setup mock data
    participant_data = MockDataFactory.gully_participant(
        id=1, user_id=2, gully_id=1, role="member"
    )

    # Configure mocks
    MockDBUtil.configure_get(mock_db, GullyParticipant, participant_data)
    # Mock is_gully_admin check to return False
    with patch("src.api.routes.gullies.is_gully_admin", AsyncMock(return_value=False)):
        # Make request
        response = test_client.put(
            "/api/participants/1",
            json={"role": "admin"},
        )

        # Verify response
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "admin" in data["detail"].lower()
