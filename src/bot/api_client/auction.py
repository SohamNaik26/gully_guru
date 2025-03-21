"""
API client for auction functionality.
Handles auction operations, contested players, and auction queue management.
"""

import logging
from typing import Dict, Any, Optional, List

from src.bot.api_client.base import BaseApiClient
from src.bot.context import manager as ctx_manager
from src.bot.api_client.onboarding import (
    get_onboarding_client as get_initialized_onboarding_client,
)

# Configure logging
logger = logging.getLogger(__name__)


class AuctionApiClient(BaseApiClient):
    """API client for auction functionality."""

    def __init__(self, api_client: Optional[BaseApiClient] = None):
        """
        Initialize the auction API client.

        Args:
            api_client: Optional API client instance
        """
        super().__init__(api_client)

    async def start_auction(self, gully_id: int) -> Dict[str, Any]:
        """
        Start auction for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Auction start response
        """
        response = await self._make_request(
            "POST", f"/api/auction/gullies/{gully_id}/start"
        )
        return response

    async def stop_auction(self, gully_id: int, context=None) -> Dict[str, Any]:
        """
        Stop auction for a gully and update context cache.

        Args:
            gully_id: Gully ID
            context: Optional context object

        Returns:
            Success response
        """
        response = await self._make_request(
            "POST", f"/api/auction/gullies/{gully_id}/stop"
        )

        # If context is provided and response was successful, update gully status in cache
        if context and response and response.get("success"):
            # Force refresh of gully data after status change
            onboarding_client = await get_initialized_onboarding_client()
            gully_data = await onboarding_client.get_gully(gully_id)
            if gully_data:
                ctx_manager.update_gully_data(context, gully_id, gully_data)

        return response

    async def get_auction_queue(self, gully_id: int) -> Dict[str, Any]:
        """
        Get all players from the auction queue for a specific gully.

        Args:
            gully_id: Gully ID

        Returns:
            List of players in the auction queue
        """
        response = await self._make_request(
            "GET", f"/api/auction/gullies/{gully_id}/auction-queue"
        )
        return response

    async def get_contested_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Get contested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with gully info and participants with their contested players
        """
        response = await self._make_request(
            "GET", f"/api/auction/gullies/{gully_id}/contested-players"
        )
        return response

    async def get_uncontested_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Get uncontested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with gully info and participants with their uncontested players
        """
        response = await self._make_request(
            "GET", f"/api/auction/gullies/{gully_id}/uncontested-players"
        )
        return response

    async def get_all_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Get all players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with gully info and participants with all their players
        """
        response = await self._make_request(
            "GET", f"/api/auction/gullies/{gully_id}/all-players"
        )
        return response

    async def update_auction_status(
        self, auction_queue_id: int, status: str, gully_id: int
    ) -> Dict[str, Any]:
        """
        Update an auction's status.

        Args:
            auction_queue_id: Auction queue ID
            status: New status for the auction
            gully_id: Gully ID

        Returns:
            Success response
        """
        response = await self._make_request(
            "PUT",
            f"/api/auction/queue/{auction_queue_id}/status",
            data={"status": status, "gully_id": gully_id},
        )
        return response

    async def resolve_contested_player(
        self,
        player_id: int,
        winning_participant_id: int,
        auction_queue_id: int,
        bid_amount: float,
    ) -> Dict[str, Any]:
        """
        Resolve a contested player by assigning it to the winning participant.

        Args:
            player_id: ID of the player
            winning_participant_id: ID of the winning participant
            auction_queue_id: ID of the auction queue item
            bid_amount: Final bid amount for the player

        Returns:
            Updated player data
        """
        payload = {"auction_queue_id": auction_queue_id, "bid_amount": bid_amount}
        response = await self._make_request(
            "POST",
            f"/api/auction/resolve-contested/{player_id}/{winning_participant_id}",
            data=payload,
        )
        return response

    async def release_players(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Release players from a participant and add them to the auction queue.

        Args:
            participant_id: ID of the participant
            player_ids: List of player IDs to release

        Returns:
            Release players response
        """
        response = await self._make_request(
            "POST",
            f"/api/auction/participants/{participant_id}/release-players",
            data={"player_ids": player_ids},
        )
        return response.get("data", {})

    async def get_next_player(self, gully_id: int) -> Dict[str, Any]:
        """
        Get the next player in the auction queue for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Next player information and eligible participants
        """
        response = await self._make_request(
            "GET", f"/api/auction/gullies/{gully_id}/next-player"
        )
        return response

    async def revert_auction(
        self, player_id: int, winning_participant_id: int, auction_queue_id: int
    ) -> Dict[str, Any]:
        """
        Revert an auction result, returning the player to the queue.

        Args:
            player_id: ID of the player
            winning_participant_id: ID of the winning participant
            auction_queue_id: ID of the auction queue item

        Returns:
            Reversion operation response
        """
        response = await self._make_request(
            "POST",
            f"/api/auction/revert/{player_id}/{winning_participant_id}",
            data={"auction_queue_id": auction_queue_id},
        )
        return response

    async def skip_player(self, gully_id: int, auction_queue_id: int) -> Dict[str, Any]:
        """
        Skip/reject a player from the auction queue.

        Args:
            gully_id: Gully ID
            auction_queue_id: Auction queue ID of the player to skip

        Returns:
            Skip player response
        """
        response = await self._make_request(
            "POST",
            f"/api/auction/gullies/{gully_id}/skip-player",
            data={"auction_queue_id": auction_queue_id},
        )
        return response


# Factory function to get auction client
async def get_auction_client(
    api_client: Optional[BaseApiClient] = None,
) -> AuctionApiClient:
    """
    Get an instance of the auction API client.

    Args:
        api_client: Optional API client instance

    Returns:
        AuctionApiClient instance
    """
    return AuctionApiClient(api_client)
