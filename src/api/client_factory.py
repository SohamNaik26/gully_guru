import logging
import httpx

from src.api.services.users import UserService
from src.api.services.gullies import GullyService
from src.api.services.players import PlayerService
from src.api.services.fantasy import FantasyService
from src.api.services.admin import AdminService

logger = logging.getLogger(__name__)


class APIClientFactory:
    """Factory for creating API service clients."""

    def __init__(self, base_url: str, auth_token: str = "test"):
        """Initialize the API client factory.

        Args:
            base_url: The base URL for the API
            auth_token: Authentication token (default: "test" for development)
        """
        # Make sure the base_url ends with /api
        if not base_url.endswith("/api"):
            base_url = f"{base_url}/api"
        self.base_url = base_url

        # Set up headers with authentication token
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

        self.client = httpx.AsyncClient(
            timeout=30.0, follow_redirects=True, headers=headers
        )
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
