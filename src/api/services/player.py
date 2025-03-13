"""
Player service for the GullyGuru API.
This module provides client methods for interacting with player-related API endpoints and database operations.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx

from sqlmodel import select

from src.api.services.base import BaseService, BaseServiceClient
from src.db.models.models import Player

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
        """Get stats for a player.

        Args:
            player_id: The ID of the player

        Returns:
            Player stats data or None if not found
        """
        response = await self._make_request("GET", f"{self.endpoint}/{player_id}/stats")
        if "error" in response:
            logger.error(f"Error getting player stats: {response['error']}")
            return None
        return response


class PlayerServiceClient(BaseServiceClient):
    """Client for interacting with player-related database operations."""

    async def get_players(
        self,
        skip: int = 0,
        limit: int = 10,
        team: Optional[str] = None,
        player_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Player]:
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
        query = select(Player)

        # Apply filters
        if team:
            query = query.where(Player.team == team)
        if player_type:
            query = query.where(Player.player_type == player_type)
        if search:
            query = query.where(Player.name.contains(search))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_player(self, player_id: int) -> Optional[Player]:
        """Get a player by ID.

        Args:
            player_id: The ID of the player

        Returns:
            Player object or None if not found
        """
        return await self.db.get(Player, player_id)

    async def get_player_by_name(self, name: str) -> Optional[Player]:
        """Get a player by name.

        Args:
            name: The name of the player

        Returns:
            Player object or None if not found
        """
        query = select(Player).where(Player.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_player(self, player_data: Dict[str, Any]) -> Player:
        """Create a new player.

        Args:
            player_data: Player data to create

        Returns:
            Created player object
        """
        player = Player(**player_data)
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player

    async def update_player(
        self, player_id: int, player_data: Dict[str, Any]
    ) -> Optional[Player]:
        """Update a player.

        Args:
            player_id: The ID of the player to update
            player_data: Player data to update

        Returns:
            Updated player object or None if not found
        """
        player = await self.db.get(Player, player_id)
        if not player:
            return None

        for key, value in player_data.items():
            setattr(player, key, value)

        await self.db.commit()
        await self.db.refresh(player)
        return player

    async def delete_player(self, player_id: int) -> bool:
        """Delete a player.

        Args:
            player_id: The ID of the player to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        player = await self.db.get(Player, player_id)
        if not player:
            return False

        await self.db.delete(player)
        await self.db.commit()
        return True
