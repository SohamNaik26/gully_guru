"""
API client for auction functionality.
Handles auction operations, contested players, and auction status.
"""

import logging
from typing import Dict, Any, Optional, List

from src.bot.api_client.base import get_api_client, BaseApiClient

# Configure logging
logger = logging.getLogger(__name__)


class AuctionApiClient:
    """API client for auction functionality."""

    def __init__(self, api_client: Optional[BaseApiClient] = None):
        """
        Initialize the auction API client.

        Args:
            api_client: Optional API client instance
        """
        self._api_client = api_client

    async def _get_client(self) -> BaseApiClient:
        """
        Get the API client instance.

        Returns:
            BaseApiClient instance
        """
        if self._api_client is None:
            self._api_client = await get_api_client()
        return self._api_client

    async def get_contested_players(self, gully_id: int) -> List[Dict[str, Any]]:
        """
        Get contested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            List of contested players if successful, empty list otherwise
        """
        client = await self._get_client()

        logger.info(f"Getting contested players for gully {gully_id}")

        # Use the auction endpoint
        response = await client.get(f"auction/gullies/{gully_id}/contested-players")

        if response and isinstance(response, list):
            logger.info(f"Got {len(response)} contested players for gully {gully_id}")
            return response
        else:
            logger.error(f"Failed to get contested players for gully {gully_id}")
            return []

    async def get_uncontested_players(self, gully_id: int) -> List[Dict[str, Any]]:
        """
        Get uncontested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            List of uncontested players if successful, empty list otherwise
        """
        client = await self._get_client()

        logger.info(f"Getting uncontested players for gully {gully_id}")

        # Use the auction endpoint
        response = await client.get(f"auction/gullies/{gully_id}/uncontested-players")

        if response and isinstance(response, list):
            logger.info(f"Got {len(response)} uncontested players for gully {gully_id}")
            return response
        else:
            logger.error(f"Failed to get uncontested players for gully {gully_id}")
            return []

    async def update_auction_status(
        self, auction_queue_id: int, status: str, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Update an auction's status.

        Args:
            auction_queue_id: Auction queue ID
            status: New status for the auction
            gully_id: Gully ID

        Returns:
            Success response if successful, None otherwise
        """
        client = await self._get_client()

        logger.info(
            f"Updating auction status for auction {auction_queue_id} to {status} in gully {gully_id}"
        )

        # Use the auction endpoint
        response = await client.put(
            f"auction/queue/{auction_queue_id}/status",
            json={"status": status, "gully_id": gully_id},
        )

        if response:
            logger.info(f"Updated auction status successfully")
            return response
        else:
            logger.error(f"Failed to update auction status")
            return None

    async def start_auction(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """
        Start auction for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Auction start response if successful, None otherwise
        """
        client = await self._get_client()

        logger.info(f"Starting auction for gully {gully_id}")

        # Use the auction endpoint
        response = await client.post(f"auction/gullies/{gully_id}/start")

        if response:
            logger.info(f"Started auction for gully {gully_id} successfully")
            return response
        else:
            logger.error(f"Failed to start auction for gully {gully_id}")
            return None

    async def resolve_contested_player(
        self, player_id: int, winning_participant_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve a contested player by assigning it to the winning participant.

        Args:
            player_id: Player ID
            winning_participant_id: ID of the winning participant

        Returns:
            Resolution response if successful, None otherwise
        """
        client = await self._get_client()

        logger.info(
            f"Resolving contested player {player_id} for participant {winning_participant_id}"
        )

        # Use the auction endpoint
        response = await client.post(
            f"auction/resolve-contested/{player_id}/{winning_participant_id}"
        )

        if response:
            logger.info(f"Resolved contested player successfully")
            return response
        else:
            logger.error(f"Failed to resolve contested player")
            return None


# Singleton instance
_auction_client = None


async def get_auction_client() -> AuctionApiClient:
    """
    Get the auction API client instance.

    Returns:
        AuctionApiClient instance
    """
    global _auction_client
    if _auction_client is None:
        api_client = await get_api_client()
        _auction_client = AuctionApiClient(api_client)
        logger.info("Initialized auction API client")

    return _auction_client
