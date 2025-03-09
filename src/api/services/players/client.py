import logging
from typing import Dict, Any, Optional, List
import httpx

from src.api.services.base import BaseService

logger = logging.getLogger(__name__)


class PlayerService(BaseService):
    """Client for interacting with player-related API endpoints."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the player service client.

        Args:
            base_url: The base URL for the API
            client: An optional httpx AsyncClient instance
        """
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/players"

    async def get_players(
        self,
        skip: int = 0,
        limit: int = 10,
        team: Optional[str] = None,
        player_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get a list of players with optional filtering.

        Args:
            skip: Number of players to skip
            limit: Maximum number of players to return
            team: Filter by team name
            player_type: Filter by player type (batsman, bowler, all-rounder, wicket-keeper)
            search: Search term for player name

        Returns:
            List of players
        """
        params = {"skip": skip, "limit": limit}
        if team:
            params["team"] = team
        if player_type:
            params["player_type"] = player_type
        if search:
            params["search"] = search

        response = await self._make_request("GET", self.endpoint, params=params)
        if "error" in response:
            logger.error(f"Error getting players: {response['error']}")
            return []
        return response

    async def get_player(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get a player by ID.

        Args:
            player_id: The ID of the player

        Returns:
            Player data or None if not found
        """
        response = await self._make_request("GET", f"{self.endpoint}/{player_id}")
        if "error" in response:
            logger.error(f"Error getting player: {response['error']}")
            return None
        return response

    async def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a player.

        Args:
            player_id: The ID of the player

        Returns:
            Player statistics or None if not found
        """
        response = await self._make_request("GET", f"{self.endpoint}/{player_id}/stats")
        if "error" in response:
            logger.error(f"Error getting player stats: {response['error']}")
            return None
        return response
