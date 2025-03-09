import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
import httpx

from src.api.services.base import BaseService

logger = logging.getLogger(__name__)


class TransferService(BaseService):
    """Client for interacting with transfer-related API endpoints."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the transfer service client.

        Args:
            base_url: The base URL for the API
            client: An optional httpx AsyncClient instance
        """
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/transfers"

    async def get_transfer_listings(
        self, status: str = "available", window_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get transfer listings.

        Args:
            status: Filter by listing status (available, completed, cancelled)
            window_id: Filter by transfer window ID

        Returns:
            List of transfer listings
        """
        params = {"status": status}
        if window_id:
            params["window_id"] = window_id

        response = await self._make_request(
            "GET", f"{self.endpoint}/listings", params=params
        )
        if "error" in response:
            logger.error(f"Error getting transfer listings: {response['error']}")
            return []
        return response

    async def get_transfer_listing(self, listing_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific transfer listing.

        Args:
            listing_id: The ID of the listing

        Returns:
            Transfer listing data or None if not found
        """
        response = await self._make_request(
            "GET", f"{self.endpoint}/listings/{listing_id}"
        )
        if "error" in response:
            logger.error(f"Error getting transfer listing: {response['error']}")
            return None
        return response

    async def get_user_listings(
        self, user_id: int, status: str = "available"
    ) -> List[Dict[str, Any]]:
        """Get listings created by a user.

        Args:
            user_id: The ID of the user
            status: Filter by listing status (available, completed, cancelled)

        Returns:
            List of transfer listings
        """
        response = await self._make_request(
            "GET", f"{self.endpoint}/user/{user_id}/listings", params={"status": status}
        )
        if "error" in response:
            logger.error(f"Error getting user listings: {response['error']}")
            return []
        return response

    async def create_transfer_listing(
        self, player_id: int, min_price: Decimal, transfer_window_id: int
    ) -> Optional[Dict[str, Any]]:
        """Create a new transfer listing.

        Args:
            player_id: The ID of the player to list
            min_price: The minimum price for the player
            transfer_window_id: The ID of the transfer window

        Returns:
            Created listing data or None if creation failed
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/listings",
            json={
                "player_id": player_id,
                "min_price": str(min_price),
                "transfer_window_id": transfer_window_id,
            },
        )
        if "error" in response:
            logger.error(f"Error creating transfer listing: {response['error']}")
            return None
        return response

    async def place_transfer_bid(
        self, listing_id: int, bid_amount: Decimal
    ) -> Dict[str, Any]:
        """Place a bid on a transfer listing.

        Args:
            listing_id: The ID of the listing
            bid_amount: The amount to bid

        Returns:
            Bid result data
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/listings/{listing_id}/bid",
            json={"amount": str(bid_amount)},
        )
        if "error" in response:
            logger.error(f"Error placing transfer bid: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def accept_transfer_bid(self, bid_id: int) -> Dict[str, Any]:
        """Accept a transfer bid.

        Args:
            bid_id: The ID of the bid to accept

        Returns:
            Acceptance result data
        """
        response = await self._make_request(
            "POST", f"{self.endpoint}/bids/{bid_id}/accept"
        )
        if "error" in response:
            logger.error(f"Error accepting transfer bid: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def cancel_transfer_listing(self, listing_id: int) -> Dict[str, Any]:
        """Cancel a transfer listing.

        Args:
            listing_id: The ID of the listing to cancel

        Returns:
            Cancellation result data
        """
        response = await self._make_request(
            "POST", f"{self.endpoint}/listings/{listing_id}/cancel"
        )
        if "error" in response:
            logger.error(f"Error cancelling transfer listing: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def get_current_transfer_window(self) -> Optional[Dict[str, Any]]:
        """Get the current transfer window.

        Returns:
            Current transfer window data or None if not found
        """
        response = await self._make_request("GET", f"{self.endpoint}/window/current")
        if "error" in response:
            logger.error(f"Error getting current transfer window: {response['error']}")
            return None
        return response
