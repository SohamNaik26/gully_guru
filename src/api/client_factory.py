import logging
import httpx

from src.api.services.users import UserService
from src.api.services.gullies import GullyService
from src.api.services.players import PlayerService
from src.api.services.transfers import TransferService
from src.api.services.fantasy import FantasyService
from src.api.services.admin import AdminService

logger = logging.getLogger(__name__)


class APIClientFactory:
    """Factory for creating API service clients."""

    def __init__(self, base_url: str):
        """Initialize the API client factory.

        Args:
            base_url: The base URL for the API
        """
        # Make sure the base_url ends with /api
        if not base_url.endswith("/api"):
            base_url = f"{base_url}/api"
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self._services = {}

    async def close(self):
        """Close the HTTP client and all service clients."""
        for service in self._services.values():
            await service.close()
        await self.client.aclose()

    @property
    def users(self) -> UserService:
        """Get the user service client.

        Returns:
            UserService: The user service client
        """
        if "users" not in self._services:
            self._services["users"] = UserService(self.base_url, self.client)
        return self._services["users"]

    @property
    def gullies(self) -> GullyService:
        """Get the gully service client.

        Returns:
            GullyService: The gully service client
        """
        if "gullies" not in self._services:
            self._services["gullies"] = GullyService(self.base_url, self.client)
        return self._services["gullies"]

    @property
    def players(self) -> PlayerService:
        """Get the player service client.

        Returns:
            PlayerService: The player service client
        """
        if "players" not in self._services:
            self._services["players"] = PlayerService(self.base_url, self.client)
        return self._services["players"]

    @property
    def transfers(self) -> TransferService:
        """Get the transfer service client.

        Returns:
            TransferService: The transfer service client
        """
        if "transfers" not in self._services:
            self._services["transfers"] = TransferService(self.base_url, self.client)
        return self._services["transfers"]

    @property
    def fantasy(self) -> FantasyService:
        """Get the fantasy service client.

        Returns:
            FantasyService: The fantasy service client
        """
        if "fantasy" not in self._services:
            self._services["fantasy"] = FantasyService(self.base_url, self.client)
        return self._services["fantasy"]

    @property
    def admin(self) -> AdminService:
        """Get the admin service client.

        Returns:
            AdminService: The admin service client
        """
        if "admin" not in self._services:
            self._services["admin"] = AdminService(self.base_url, self.client)
        return self._services["admin"]

    # Convenience methods to directly access common user methods
    async def get_user(self, telegram_id: int):
        """Get a user by Telegram ID."""
        return await self.users.get_user(telegram_id)

    async def get_user_by_id(self, user_id: int):
        """Get a user by database ID."""
        return await self.users.get_user_by_id(user_id)

    async def update_gully_participant_role(self, participant_id: int, role: str):
        """Update a gully participant's role."""
        return await self.gullies.update_gully_participant_role(participant_id, role)

    async def get_user_gully_participation(self, user_id: int, gully_id: int):
        """Get a user's participation in a gully."""
        return await self.gullies.get_user_gully_participation(user_id, gully_id)

    async def get_user_gully_participations(self, user_id: int):
        """Get all of a user's gully participations."""
        return await self.gullies.get_user_gully_participations(user_id)

    async def set_active_gully(self, participant_id: int):
        """Set a gully as active for a user."""
        return await self.gullies.set_active_gully(participant_id)

    async def add_user_to_gully(
        self, user_id: int, gully_id: int, role: str = "member"
    ):
        """Add a user to a gully."""
        return await self.gullies.add_user_to_gully(user_id, gully_id, role)
