"""
API client module for the GullyGuru API.
This module provides a factory for creating API service clients and a global API client instance.
"""

import logging
import os
import httpx

from src.api.services.fantasy import FantasyService
from src.api.services.admin import AdminService
from src.api.services.gully import GullyService
from src.api.services.player import PlayerService
from src.api.services.user import UserService
from src.utils.config import settings

logger = logging.getLogger(__name__)


class APIClient:
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

    @property
    def gully(self) -> GullyService:
        """Get the gully service client.

        Returns:
            GullyService: The gully service client
        """
        if "gully" not in self._services:
            self._services["gully"] = GullyService(self.base_url, self.client)
        return self._services["gully"]

    @property
    def player(self) -> PlayerService:
        """Get the player service client.

        Returns:
            PlayerService: The player service client
        """
        if "player" not in self._services:
            self._services["player"] = PlayerService(self.base_url, self.client)
        return self._services["player"]

    @property
    def user(self) -> UserService:
        """Get the user service client.

        Returns:
            UserService: The user service client
        """
        if "user" not in self._services:
            self._services["user"] = UserService(self.base_url, self.client)
        return self._services["user"]


# Check if we're in a test environment
is_test_environment = os.environ.get("TEST_MODE", "").lower() == "true"

# Create global API client
api_base_url = settings.API_BASE_URL
if not api_base_url.endswith("/api"):
    api_base_url = f"{api_base_url}/api"

if is_test_environment:
    logger.info("Test environment detected - using mock API client")
    # In test mode, we'll use a special test URL that won't affect production
    api_base_url = "http://testserver/api"

logger.info(f"Initializing API client with base URL: {api_base_url}")
# Use test token for authentication in development
api_client = APIClient(base_url=api_base_url, auth_token="test")
