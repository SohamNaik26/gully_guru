import logging
import httpx
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

from src.utils.config import settings

logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the GullyGuru API."""

    def __init__(self, base_url: str = None):
        """Initialize the API client."""
        self.base_url = (
            base_url or f"http://{settings.API_HOST}:{settings.API_PORT}/api"
        )
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    # User endpoints
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by Telegram ID."""
        try:
            response = await self.client.get(
                f"{self.base_url}/users/telegram/{telegram_id}"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user."""
        try:
            response = await self.client.post(f"{self.base_url}/users/", json=user_data)
            if response.status_code == 201:
                return response.json()
            logger.error(f"Error creating user: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    # Player endpoints
    async def get_players(
        self,
        skip: int = 0,
        limit: int = 10,
        team: Optional[str] = None,
        player_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get players with optional filtering."""
        try:
            params = {"skip": skip, "limit": limit}
            if team:
                params["team"] = team
            if player_type:
                params["player_type"] = player_type
            if search:
                params["search"] = search

            response = await self.client.get(f"{self.base_url}/players/", params=params)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting players: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error getting players: {e}")
            return []

    async def get_player(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get a player by ID."""
        try:
            response = await self.client.get(f"{self.base_url}/players/{player_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting player: {e}")
            return None

    async def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a player."""
        try:
            response = await self.client.get(
                f"{self.base_url}/players/{player_id}/stats"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return None

    # Team management endpoints
    async def get_user_team(
        self, user_id: int, game_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get a user's team."""
        try:
            params = {}
            if game_id:
                params["game_id"] = game_id

            response = await self.client.get(
                f"{self.base_url}/users/{user_id}/team", params=params
            )
            return response
        except Exception as e:
            logger.error(f"Error getting user team: {e}")
            return {"success": False, "error": str(e)}

    async def buy_player(
        self, user_id: int, player_id: int, price: Decimal
    ) -> Optional[Dict[str, Any]]:
        """Buy a player for a user's team."""
        try:
            response = await self.client.post(
                f"{self.base_url}/fantasy/buy",
                json={
                    "user_id": user_id,
                    "player_id": player_id,
                    "price": float(price),
                },
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error buying player: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error buying player: {e}")
            return None

    async def set_captain(self, user_id: int, player_id: int) -> bool:
        """Set a player as team captain."""
        try:
            response = await self.client.post(
                f"{self.base_url}/fantasy/captain",
                json={"user_id": user_id, "player_id": player_id},
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error setting captain: {e}")
            return False

    # Auction endpoints
    async def get_auction_status(self, game_id: Optional[int] = None) -> Dict[str, Any]:
        """Get current auction status."""
        try:
            params = {}
            if game_id:
                params["game_id"] = game_id

            response = await self.client.get(
                f"{self.base_url}/fantasy/auction/current", params=params
            )
            return response
        except Exception as e:
            logger.error(f"Error getting auction status: {e}")
            return None

    async def place_bid(
        self, user_id: int, player_id: int, amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """Place a bid in the auction."""
        try:
            response = await self.client.post(
                f"{self.base_url}/auctions/bid",
                json={
                    "user_id": user_id,
                    "player_id": player_id,
                    "amount": float(amount),
                },
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error placing bid: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error placing bid: {e}")
            return None

    # Match endpoints
    async def get_matches(
        self, upcoming: bool = True, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get upcoming or past matches."""
        try:
            params = {"upcoming": str(upcoming).lower(), "limit": limit}
            response = await self.client.get(f"{self.base_url}/matches/", params=params)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting matches: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error getting matches: {e}")
            return []

    async def get_match(self, match_id: int) -> Optional[Dict[str, Any]]:
        """Get details for a specific match."""
        try:
            response = await self.client.get(f"{self.base_url}/matches/{match_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting match: {e}")
            return None

    async def submit_prediction(
        self, user_id: int, match_id: int, prediction: str
    ) -> bool:
        """Submit a match prediction."""
        try:
            response = await self.client.post(
                f"{self.base_url}/matches/predict",
                json={
                    "user_id": user_id,
                    "match_id": match_id,
                    "prediction": prediction,
                },
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error submitting prediction: {e}")
            return False

    # Leaderboard endpoints
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the global leaderboard."""
        try:
            response = await self.client.get(
                f"{self.base_url}/stats/leaderboard", params={"limit": limit}
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting leaderboard: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    # Admin endpoints
    async def get_system_stats(self) -> Optional[Dict[str, Any]]:
        """Get system statistics (admin only)."""
        try:
            response = await self.client.get(f"{self.base_url}/admin/stats")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return None

    async def assign_player_to_user(
        self, user_id: int, player_id: int, price: float
    ) -> Dict[str, Any]:
        """Assign a player to a user's team."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/fantasy/team/add-player",
                json={"user_id": user_id, "player_id": player_id, "price": price},
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {
                "success": False,
                "error": response.json().get("detail", "Unknown error"),
            }
        except Exception as e:
            logger.error(f"Error assigning player to user: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by ID."""
        try:
            response = await self.client.get(f"{self.base_url}/users/{user_id}")

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    # Transfer endpoints
    async def get_transfer_listings(
        self, status: str = "available", window_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get all transfer listings with the specified status."""
        try:
            params = {"status": status}
            if window_id:
                params["window_id"] = window_id

            response = await self.client.get(
                f"{self.base_url}/transfers/listings", params=params
            )

            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting transfer listings: {e}")
            return []

    async def get_transfer_listing(self, listing_id: int) -> Optional[Dict[str, Any]]:
        """Get details of a specific transfer listing."""
        try:
            response = await self.client.get(
                f"{self.base_url}/transfers/listings/{listing_id}"
            )

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting transfer listing: {e}")
            return None

    async def get_user_listings(
        self, user_id: int, status: str = "available"
    ) -> List[Dict[str, Any]]:
        """Get all transfer listings created by a specific user."""
        try:
            response = await self.client.get(
                f"{self.base_url}/transfers/user-listings/{user_id}",
                params={"status": status},
            )

            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting user listings: {e}")
            return []

    async def create_transfer_listing(
        self, player_id: int, min_price: Decimal, transfer_window_id: int
    ) -> Optional[Dict[str, Any]]:
        """Create a new transfer listing."""
        try:
            response = await self.client.post(
                f"{self.base_url}/transfers/list",
                json={"player_id": player_id, "min_price": float(min_price)},
            )

            if response.status_code == 200:
                return response.json()
            logger.error(f"Error creating transfer listing: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error creating transfer listing: {e}")
            return None

    async def place_transfer_bid(
        self, listing_id: int, bid_amount: Decimal
    ) -> Dict[str, Any]:
        """Place a bid on a transfer listing."""
        try:
            response = await self.client.post(
                f"{self.base_url}/transfers/bid",
                json={"listing_id": listing_id, "bid_amount": float(bid_amount)},
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {
                "success": False,
                "error": response.json().get("detail", "Unknown error"),
            }
        except Exception as e:
            logger.error(f"Error placing transfer bid: {e}")
            return {"success": False, "error": str(e)}

    async def accept_transfer_bid(self, bid_id: int) -> Dict[str, Any]:
        """Accept a transfer bid."""
        try:
            response = await self.client.post(
                f"{self.base_url}/transfers/accept-bid/{bid_id}"
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {
                "success": False,
                "error": response.json().get("detail", "Unknown error"),
            }
        except Exception as e:
            logger.error(f"Error accepting transfer bid: {e}")
            return {"success": False, "error": str(e)}

    async def cancel_transfer_listing(self, listing_id: int) -> Dict[str, Any]:
        """Cancel a transfer listing."""
        try:
            response = await self.client.post(
                f"{self.base_url}/transfers/cancel-listing/{listing_id}"
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {
                "success": False,
                "error": response.json().get("detail", "Unknown error"),
            }
        except Exception as e:
            logger.error(f"Error cancelling transfer listing: {e}")
            return {"success": False, "error": str(e)}

    async def get_current_transfer_window(self) -> Optional[Dict[str, Any]]:
        """Get the current transfer window."""
        try:
            response = await self.client.get(f"{self.base_url}/transfers/current")

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting current transfer window: {e}")
            return None

    async def validate_user_team(self, user_id: int) -> Dict[str, Any]:
        """Validate a user's team composition."""
        try:
            response = await self.client.post(
                f"{self.base_url}/fantasy/validate-team", params={"user_id": user_id}
            )

            if response.status_code == 200:
                return response.json()
            return {
                "valid": False,
                "message": response.json().get("detail", "Unknown error"),
            }
        except Exception as e:
            logger.error(f"Error validating user team: {e}")
            return {"valid": False, "message": str(e)}

    # Game management endpoints
    async def create_gully(
        self,
        name: str,
        telegram_group_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Create a new gully instance."""
        try:
            response = await self.client.post(
                f"{self.base_url}/gullies",
                json={
                    "name": name,
                    "telegram_group_id": telegram_group_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error creating gully: {e}")
            return {"success": False, "error": str(e)}

    async def get_gully_by_group(self, group_id: int) -> Dict[str, Any]:
        """Get a gully by Telegram group ID."""
        try:
            response = await self.client.get(
                f"{self.base_url}/gullies/group/{group_id}"
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error getting gully by group: {e}")
            return None

    async def join_game(
        self, game_id: int, user_id: int, team_name: str
    ) -> Dict[str, Any]:
        """Join a game as a participant."""
        try:
            response = await self.client.post(
                f"{self.base_url}/games/{game_id}/join",
                json={"user_id": user_id, "team_name": team_name},
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error joining game: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_games(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all games a user is participating in."""
        try:
            response = await self.client.get(f"{self.base_url}/users/{user_id}/games")
            return response.json()
        except Exception as e:
            logger.error(f"Error getting user games: {e}")
            return []

    async def get_game_participants(self, game_id: int) -> List[Dict[str, Any]]:
        """Get all participants in a game."""
        try:
            response = await self.client.get(
                f"{self.base_url}/games/{game_id}/participants"
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error getting game participants: {e}")
            return []

    async def set_active_game(self, user_id: int, game_id: int) -> Dict[str, Any]:
        """Set a user's active game."""
        try:
            response = await self.client.patch(
                f"{self.base_url}/users/{user_id}", json={"active_game_id": game_id}
            )
            return response
        except Exception as e:
            logger.error(f"Error setting active game: {e}")
            return {"success": False, "error": str(e)}
