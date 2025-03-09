import logging
from typing import Dict, Any, Optional
from decimal import Decimal
import httpx

from src.api.services.base import BaseService

logger = logging.getLogger(__name__)


class FantasyService(BaseService):
    """Client for interacting with fantasy-related API endpoints."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the fantasy service client.

        Args:
            base_url: The base URL for the API
            client: An optional httpx AsyncClient instance
        """
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/fantasy"

    async def get_user_team(
        self, user_id: int, game_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get a user's fantasy team.

        Args:
            user_id: The ID of the user
            game_id: The ID of the game (optional)

        Returns:
            User's team data
        """
        params = {}
        if game_id:
            params["game_id"] = game_id

        response = await self._make_request(
            "GET", f"{self.endpoint}/teams/user/{user_id}", params=params
        )
        if "error" in response:
            logger.error(f"Error getting user team: {response['error']}")
            return {"players": [], "captain_id": None, "budget": 0}
        return response

    async def buy_player(
        self, user_id: int, player_id: int, price: Decimal
    ) -> Optional[Dict[str, Any]]:
        """Buy a player for a user's team.

        Args:
            user_id: The ID of the user
            player_id: The ID of the player to buy
            price: The price to pay for the player

        Returns:
            Purchase result data or None if purchase failed
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/teams/user/{user_id}/buy",
            json={"player_id": player_id, "price": str(price)},
        )
        if "error" in response:
            logger.error(f"Error buying player: {response['error']}")
            return None
        return response

    async def set_captain(self, user_id: int, player_id: int) -> bool:
        """Set a player as captain.

        Args:
            user_id: The ID of the user
            player_id: The ID of the player to set as captain

        Returns:
            True if successful, False otherwise
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/teams/user/{user_id}/captain",
            json={"player_id": player_id},
        )
        if "error" in response:
            logger.error(f"Error setting captain: {response['error']}")
            return False
        return True

    async def validate_user_team(self, user_id: int) -> Dict[str, Any]:
        """Validate a user's team.

        Args:
            user_id: The ID of the user

        Returns:
            Validation result data
        """
        response = await self._make_request(
            "GET", f"{self.endpoint}/teams/user/{user_id}/validate"
        )
        if "error" in response:
            logger.error(f"Error validating user team: {response['error']}")
            return {"valid": False, "errors": [response["error"]]}
        return response
