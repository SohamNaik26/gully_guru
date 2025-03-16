"""
Squad API client for GullyGuru bot.
Handles all squad-related API calls.
"""

import logging
from typing import Dict, Any, List, Optional

from src.bot.api_client.base import BaseApiClient

# Configure logging
logger = logging.getLogger(__name__)


class SquadApiClient(BaseApiClient):
    """API client for squad-related endpoints."""

    async def get_draft_squad(self, participant_id: int) -> Dict[str, Any]:
        """
        Get the draft squad for a participant.

        Args:
            participant_id: Participant ID

        Returns:
            Draft squad data
        """
        endpoint = f"/fantasy/draft-squad/{participant_id}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            return response.get("data", {})
        else:
            logger.error(f"Failed to get draft squad: {response.get('error')}")
            return {}

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
        # Updated endpoint based on API documentation
        endpoint = f"/players/?limit={limit}&offset={offset}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            # Handle the paginated response format
            data = response.get("data", {})
            if isinstance(data, dict) and "items" in data:
                return data.get("items", [])
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected response format: {data}")
                return []
        else:
            logger.error(f"Error getting players: {response.get('error')}")
            return []

    async def add_multiple_players_to_draft(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Add multiple players to a participant's draft squad.

        Args:
            participant_id: Participant ID
            player_ids: List of player IDs to add

        Returns:
            Response with results of the operation
        """
        if not participant_id or not player_ids:
            logger.error("Both participant_id and player_ids are required")
            return {"success": False, "error": "Missing required parameters"}

        endpoint = f"/fantasy/draft-squad/{participant_id}/add"
        response = await self._make_request(
            "POST", endpoint, json={"player_ids": player_ids}
        )

        if response.get("success"):
            return {"success": True, "data": response.get("data", {})}
        else:
            logger.error(f"Error adding players to draft: {response.get('error')}")
            return {"success": False, "error": response.get("error")}

    async def remove_multiple_players_from_draft(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Remove multiple players from a participant's draft squad.

        Args:
            participant_id: Participant ID
            player_ids: List of player IDs to remove

        Returns:
            Response with results of the operation
        """
        if not participant_id or not player_ids:
            logger.error("Both participant_id and player_ids are required")
            return {"success": False, "error": "Missing required parameters"}

        endpoint = f"/fantasy/draft-squad/{participant_id}/remove"
        response = await self._make_request(
            "POST", endpoint, json={"player_ids": player_ids}
        )

        if response.get("success"):
            return {"success": True, "data": response.get("data", {})}
        else:
            logger.error(f"Error removing players from draft: {response.get('error')}")
            return {"success": False, "error": response.get("error")}

    async def update_draft_squad(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Update a participant's entire draft squad.
        This can be used to finalize the squad by setting all desired players at once.

        Args:
            participant_id: Participant ID
            player_ids: Complete list of player IDs for the squad

        Returns:
            Response with results of the operation
        """
        if not participant_id:
            logger.error("participant_id is required")
            return {"success": False, "error": "Missing required parameter"}

        endpoint = f"/fantasy/draft-squad/{participant_id}"
        response = await self._make_request(
            "PUT", endpoint, json={"player_ids": player_ids}
        )

        if response.get("success"):
            return {"success": True, "data": response.get("data", {})}
        else:
            logger.error(f"Error updating draft squad: {response.get('error')}")
            return {"success": False, "error": response.get("error")}


async def get_squad_client() -> SquadApiClient:
    """
    Get an instance of the squad API client.

    Returns:
        SquadApiClient instance
    """
    return SquadApiClient()
