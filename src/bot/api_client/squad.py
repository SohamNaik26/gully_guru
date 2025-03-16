"""
API client for squad-related operations.
"""

import logging
from typing import Dict, Any, List, Optional

from src.bot.api_client.base import get_api_client

logger = logging.getLogger(__name__)


class SquadClient:
    """Client for squad-related API operations."""

    def __init__(self, api_client):
        """Initialize the squad client with the API client."""
        self.api_client = api_client

    async def get_draft_squad(self, participant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the draft squad for a participant.

        Args:
            participant_id: The participant ID

        Returns:
            The draft squad data or None if not found
        """
        try:
            response = await self.api_client.get(f"/squads/draft/{participant_id}")
            return response
        except Exception as e:
            logger.error(f"Error getting draft squad: {e}")
            return None

    async def get_available_players(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get available players for squad selection.

        Args:
            limit: Maximum number of players to return
            offset: Offset for pagination

        Returns:
            List of player data
        """
        try:
            response = await self.api_client.get(
                f"/players/available?limit={limit}&offset={offset}"
            )
            return response or []
        except Exception as e:
            logger.error(f"Error getting available players: {e}")
            return []

    async def add_player_to_draft(
        self, participant_id: int, player_id: int
    ) -> Dict[str, Any]:
        """
        Add a player to a draft squad.

        Args:
            participant_id: The participant ID
            player_id: The player ID

        Returns:
            Response data with success status
        """
        try:
            response = await self.api_client.post(
                f"/squads/draft/{participant_id}/players", json={"player_id": player_id}
            )
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Error adding player to draft: {e}")
            return {"success": False, "error": str(e)}

    async def add_multiple_players_to_draft(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Add multiple players to a draft squad in a single API call.

        Args:
            participant_id: Participant ID
            player_ids: List of player IDs to add

        Returns:
            Response with results of the operation
        """
        if not participant_id or not player_ids:
            logger.error("Both participant_id and player_ids are required")
            return {"success": False, "error": "Missing required parameters"}

        try:
            response = await self.api_client.post(
                f"/squads/draft/{participant_id}/players",
                json={"player_ids": player_ids},
            )
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Error adding players to draft: {e}")
            return {"success": False, "error": str(e)}
