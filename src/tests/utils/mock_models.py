"""
Mock models for testing.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional


class MockUser:
    """Mock User model for testing."""

    def __init__(
        self,
        id: int = 1,
        telegram_id: int = 12345678,
        username: str = "test_user",
        full_name: str = "Test User",
        created_at: datetime = datetime.now(timezone.utc),
        updated_at: datetime = datetime.now(timezone.utc),
    ):
        self.id = id
        self.telegram_id = telegram_id
        self.username = username
        self.full_name = full_name
        self.created_at = created_at
        self.updated_at = updated_at
        self.gullies = []  # Mock relationship

    def add_gully(self, gully):
        """Add a gully to the user's gullies."""
        self.gullies.append(gully)


class MockGully:
    """Mock Gully model for testing."""

    def __init__(
        self,
        id: int = 1,
        name: str = "Test Gully",
        telegram_group_id: int = 87654321,
        created_at: datetime = datetime.now(timezone.utc),
        updated_at: datetime = datetime.now(timezone.utc),
    ):
        self.id = id
        self.name = name
        self.telegram_group_id = telegram_group_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.participants = []  # Mock relationship
        self.user_players = []  # Mock relationship
        self.users = []  # Mock relationship

    def add_participant(self, participant):
        """Add a participant to the gully."""
        self.participants.append(participant)

    def add_user(self, user):
        """Add a user to the gully."""
        self.users.append(user)

    def add_user_player(self, user_player):
        """Add a user_player to the gully."""
        self.user_players.append(user_player)


class MockGullyParticipant:
    """Mock GullyParticipant model for testing."""

    def __init__(
        self,
        id: int = 1,
        user_id: int = 1,
        gully_id: int = 1,
        team_name: str = "Test Team",
        budget: Decimal = Decimal("120.0"),
        points: int = 0,
        role: str = "member",
        created_at: datetime = datetime.now(timezone.utc),
        updated_at: datetime = datetime.now(timezone.utc),
    ):
        self.id = id
        self.user_id = user_id
        self.gully_id = gully_id
        self.team_name = team_name
        self.budget = budget
        self.points = points
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
        self.user = None  # Will be set if needed
        self.gully = None  # Will be set if needed

    def set_gully(self, gully):
        """Set the gully relationship."""
        self.gully = gully

    def set_user(self, user):
        """Set the user relationship."""
        self.user = user


class MockPlayer:
    """Mock Player model for testing."""

    def __init__(
        self,
        id: int = 1,
        name: str = "Test Player",
        team: str = "Test Team",
        player_type: str = "BAT",
        base_price: Optional[Decimal] = Decimal("1.0"),
        sold_price: Optional[Decimal] = Decimal("2.0"),
        season: int = 2025,
        created_at: datetime = datetime.now(timezone.utc),
        updated_at: datetime = datetime.now(timezone.utc),
    ):
        self.id = id
        self.name = name
        self.team = team
        self.player_type = player_type
        self.base_price = base_price
        self.sold_price = sold_price
        self.season = season
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_player = None  # Will be set if needed

    def set_user_player(self, user_player):
        """Set the user_player relationship."""
        self.user_player = user_player


class MockUserPlayer:
    """Mock UserPlayer model for testing."""

    def __init__(
        self,
        id: int = 1,
        user_id: int = 1,
        player_id: int = 1,
        gully_id: int = 1,
        purchase_price: Decimal = Decimal("2.0"),
        purchase_date: datetime = datetime.now(timezone.utc),
        is_captain: bool = False,
        is_vice_captain: bool = False,
        is_playing_xi: bool = False,
        created_at: datetime = datetime.now(timezone.utc),
        updated_at: datetime = datetime.now(timezone.utc),
    ):
        self.id = id
        self.user_id = user_id
        self.player_id = player_id
        self.gully_id = gully_id
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.is_captain = is_captain
        self.is_vice_captain = is_vice_captain
        self.is_playing_xi = is_playing_xi
        self.created_at = created_at
        self.updated_at = updated_at
        self.user = None  # Will be set if needed
        self.player = None  # Will be set if needed
        self.gully = None  # Will be set if needed

    def set_user(self, user):
        """Set the user relationship."""
        self.user = user

    def set_player(self, player):
        """Set the player relationship."""
        self.player = player

    def set_gully(self, gully):
        """Set the gully relationship."""
        self.gully = gully
