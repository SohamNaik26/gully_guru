import logging
import httpx
from typing import Dict, Any, Optional, List
from decimal import Decimal

from src.utils.config import settings

logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the GullyGuru API."""

    def __init__(self, base_url: str = None):
        """Initialize the API client."""
        self.base_url = base_url or f"http://{settings.API_HOST}:{settings.API_PORT}"
        # Make sure the base_url ends with /api
        if not self.base_url.endswith("/api"):
            self.base_url = f"{self.base_url}/api"
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
            # Map 'name' to 'full_name' if it exists
            if "name" in user_data and "full_name" not in user_data:
                user_data["full_name"] = user_data.pop("name")

            response = await self.client.post(f"{self.base_url}/users/", json=user_data)
            if response.status_code == 201:
                return response.json()
            logger.error(f"Error creating user: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def update_user(
        self, telegram_id: int, user_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing user."""
        try:
            # Map 'name' to 'full_name' if it exists
            if "name" in user_data and "full_name" not in user_data:
                user_data["full_name"] = user_data.pop("name")

            response = await self.client.patch(
                f"{self.base_url}/users/telegram/{telegram_id}", json=user_data
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error updating user: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

    async def delete_user(self, telegram_id: int) -> bool:
        """Delete a user by Telegram ID."""
        try:
            response = await self.client.delete(
                f"{self.base_url}/users/telegram/{telegram_id}"
            )
            if response.status_code == 204:
                logger.info(f"User with telegram_id {telegram_id} deleted successfully")
                return True
            logger.error(f"Error deleting user: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

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
        start_date: str,
        end_date: str,
    ) -> Optional[Dict[str, Any]]:
        """Create a new gully."""
        try:
            response = await self.client.post(
                f"{self.base_url}/gullies/",
                params={
                    "name": name,
                    "telegram_group_id": telegram_group_id,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error creating gully: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error creating gully: {e}")
            return None

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

    async def get_gully_by_chat_id(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get a gully by its Telegram chat ID."""
        try:
            response = await self.client.get(f"{self.base_url}/gullies/group/{chat_id}")
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting gully by chat ID {chat_id}: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting gully by chat ID {chat_id}: {e}")
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
            response = await self.client.post(
                f"{self.base_url}/users/{user_id}/active-game",
                json={"game_id": game_id},
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error setting active game: {e}")
            return {"success": False, "error": str(e)}

    async def get_round_zero_status(self) -> Optional[Dict[str, Any]]:
        """Get the status of Round 0 submissions."""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/auctions/round-zero-status"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting Round 0 status: {str(e)}")
            return None

    async def get_user_squad_submission(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user's squad submission."""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/auctions/users/{user_id}/squad"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting user squad submission: {str(e)}")
            return None

    async def submit_squad(self, user_id: int, player_ids: List[int]) -> bool:
        """Submit a squad for Round 0."""
        try:
            data = {"player_ids": player_ids}
            response = await self.client.post(
                f"{self.base_url}/api/auctions/users/{user_id}/submit-squad", json=data
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error submitting squad: {str(e)}")
            return False

    async def get_user_permissions(
        self, user_id: int, gully_id: int
    ) -> List[Dict[str, Any]]:
        """Get user permissions in a gully."""
        url = f"{self.base_url}/admin/permissions/{gully_id}/{user_id}"
        return await self._make_request("GET", url)

    async def get_gully_admins(self, gully_id: int) -> List[Dict[str, Any]]:
        """Get all admins for a gully."""
        url = f"{self.base_url}/admin/admins/{gully_id}"
        return await self._make_request("GET", url)

    async def assign_admin_role(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Assign admin role to a user in a gully."""
        # Get the user's participation in the gully
        participation = await self.get_user_gully_participation(user_id, gully_id)
        if not participation:
            # User is not in the gully yet, add them first
            add_result = await self.add_user_to_gully(user_id, gully_id)
            if not add_result.get("success"):
                return {"success": False, "error": add_result.get("error")}
            participation = add_result.get("participant")

        # Update the role to admin
        updated = await self.update_gully_participant_role(participation["id"], "admin")
        if not updated:
            return {"success": False, "error": "Failed to update role"}

        return {"success": True, "participant": updated}

    async def remove_admin_role(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Remove admin role from a user in a gully."""
        try:
            url = f"{self.base_url}/admin/roles/{gully_id}/{user_id}"
            response = await self.client.delete(url)

            if response.status_code == 200:
                logger.info(
                    f"Successfully removed admin role from user {user_id} in gully {gully_id}"
                )
                return response.json()
            else:
                logger.error(f"Error removing admin role: {response.text}")
                return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Error removing admin role: {e}")
            return {"success": False, "error": str(e)}

    async def assign_admin_permission(
        self, user_id: int, gully_id: int, permission_type: str
    ) -> Dict[str, Any]:
        """Assign a specific admin permission to a user."""
        url = (
            f"{self.base_url}/admin/permissions/{gully_id}/{user_id}/{permission_type}"
        )
        return await self._make_request("POST", url)

    async def remove_admin_permission(
        self, user_id: int, gully_id: int, permission_type: str
    ) -> Dict[str, Any]:
        """Remove a specific admin permission from a user."""
        url = (
            f"{self.base_url}/admin/permissions/{gully_id}/{user_id}/{permission_type}"
        )
        return await self._make_request("DELETE", url)

    async def nominate_admin(self, nominee_id: int, gully_id: int) -> Dict[str, Any]:
        """Nominate a user to become an admin."""
        url = f"{self.base_url}/admin/nominate/{gully_id}/{nominee_id}"
        return await self._make_request("POST", url)

    async def generate_invite_link(
        self, gully_id: int, expiration_hours: int = 24
    ) -> Dict[str, Any]:
        """Generate an invite link for a gully."""
        url = f"{self.base_url}/admin/invite-link/{gully_id}"
        params = {"expiration_hours": expiration_hours}
        return await self._make_request("POST", url, params=params)

    async def is_admin_anywhere(self, user_id: int) -> bool:
        """Check if a user is an admin in any gully."""
        try:
            url = f"{self.base_url}/admin/is-admin-anywhere/{user_id}"
            result = await self._make_request("GET", url)
            return result.get("is_admin", False)
        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return False

    async def is_user_in_gully(self, user_id: int, gully_id: int) -> bool:
        """Check if a user is a member of a specific gully."""
        participation = await self.get_user_gully_participation(user_id, gully_id)
        return participation is not None

    async def start_auction_round_zero(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Start Round 0 (initial squad submission) for a gully."""
        try:
            response = await self.client.post(
                f"{self.base_url}/auctions/start-round-zero",
                json={"gully_id": gully_id},
            )
            if response.status_code in (200, 201):
                return response.json()
            logger.error(f"Error starting auction round zero: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error starting auction round zero: {e}")
            return None

    async def start_auction_round_one(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Start Round 1 (contested players auction) for a gully."""
        try:
            response = await self.client.post(
                f"{self.base_url}/auctions/start-round-one", json={"gully_id": gully_id}
            )
            if response.status_code in (200, 201):
                return response.json()
            logger.error(f"Error starting auction round one: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error starting auction round one: {e}")
            return None

    async def next_auction_player(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Move to the next player in the auction."""
        try:
            response = await self.client.post(
                f"{self.base_url}/auctions/next-player", json={"gully_id": gully_id}
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error moving to next auction player: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error moving to next auction player: {e}")
            return None

    async def end_auction_round(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """End the current auction round."""
        try:
            response = await self.client.post(
                f"{self.base_url}/auctions/end-round", json={"gully_id": gully_id}
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error ending auction round: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error ending auction round: {e}")
            return None

    async def complete_auction(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Complete the entire auction process."""
        try:
            response = await self.client.post(
                f"{self.base_url}/auctions/complete", json={"gully_id": gully_id}
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error completing auction: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error completing auction: {e}")
            return None

    async def get_gully_participant(
        self, user_id: int, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a user's participation details in a specific gully."""
        try:
            response = await self.client.get(
                f"{self.base_url}/gullies/{gully_id}/participants/{user_id}"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting gully participant: {e}")
            return None

    async def get_all_gullies(self) -> List[Dict[str, Any]]:
        """Get all gullies."""
        try:
            response = await self.client.get(f"{self.base_url}/gullies/")
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting all gullies: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error getting all gullies: {e}")
            return []

    async def get_gully(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Get a gully by ID."""
        try:
            response = await self.client.get(f"{self.base_url}/gullies/{gully_id}")
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting gully {gully_id}: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting gully {gully_id}: {e}")
            return None

    async def get_user_gully_participations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all gullies a user is participating in."""
        try:
            response = await self.client.get(
                f"{self.base_url}/gullies/user-gullies/{user_id}"
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting user gully participations: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error getting user gully participations: {e}")
            return []

    async def add_user_to_gully(
        self, user_id: int, gully_id: int, role: str = "member"
    ) -> Optional[Dict[str, Any]]:
        """Add a user to a gully."""
        try:
            response = await self.client.post(
                f"{self.base_url}/gullies/participants/{gully_id}/{user_id}",
                params={"role": role},
            )
            if response.status_code in [200, 201]:
                return response.json()
            logger.error(f"Error adding user to gully: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error adding user to gully: {e}")
            return None

    async def set_active_gully(
        self, user_id: int, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """Set a gully as the active gully for a user."""
        try:
            response = await self.client.put(
                f"{self.base_url}/gullies/participants/{gully_id}/{user_id}/activate"
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error setting active gully: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error setting active gully: {e}")
            return None

    async def get_gully_participants(
        self, gully_id: int, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all participants in a gully."""
        try:
            response = await self.client.get(
                f"{self.base_url}/gullies/participants/{gully_id}",
                params={"skip": skip, "limit": limit},
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error getting gully participants: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error getting gully participants: {e}")
            return []

    async def _make_request(
        self,
        method: str,
        url: str,
        json: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make a request to the API with error handling."""
        try:
            if method == "GET":
                response = await self.client.get(url, params=params)
            elif method == "POST":
                response = await self.client.post(url, json=json, params=params)
            elif method == "PUT":
                response = await self.client.put(url, json=json, params=params)
            elif method == "DELETE":
                response = await self.client.delete(url, params=params)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return {"success": False, "error": f"Unsupported HTTP method: {method}"}

            if response.status_code in (200, 201, 204):
                if response.status_code == 204:  # No content
                    return {"success": True}
                return response.json()
            else:
                logger.error(f"API request failed: {response.text}")
                return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return {"success": False, "error": str(e)}

    # GullyParticipant endpoints
    async def get_user_gully_participation(
        self, user_id: int, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a user's participation in a specific gully."""
        try:
            # Get all participations for the user
            participations = await self.get_user_gully_participations(user_id)
            if not participations:
                return None

            # Find the one for this gully
            for participation in participations:
                if participation.get("gully_id") == gully_id:
                    return participation

            return None
        except Exception as e:
            logger.error(f"Error getting user gully participation: {e}")
            return None

    async def create_gully_participant(
        self, participant_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new gully participant."""
        try:
            response = await self.client.post(
                f"{self.base_url}/users/gully-participants", json=participant_data
            )
            if response.status_code == 201:
                return response.json()
            logger.error(f"Error creating gully participant: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error creating gully participant: {e}")
            return None

    async def complete_registration(
        self, participant_id: int
    ) -> Optional[Dict[str, Any]]:
        """Mark a user's registration as complete for a gully."""
        try:
            response = await self.client.put(
                f"{self.base_url}/users/gully-participants/{participant_id}/complete-registration"
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error completing registration: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error completing registration: {e}")
            return None

    async def update_gully_participant_role(
        self, participant_id: int, role: str
    ) -> Optional[Dict[str, Any]]:
        """Update a gully participant's role."""
        try:
            response = await self.client.put(
                f"{self.base_url}/users/gully-participants/{participant_id}/role",
                json={"role": role},
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Error updating gully participant role: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error updating gully participant role: {e}")
            return None
