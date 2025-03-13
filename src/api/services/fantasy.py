"""
Fantasy service for the GullyGuru API.
This module provides client methods for interacting with fantasy-related API endpoints and database operations.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone
import httpx

from sqlalchemy import update, func
from sqlmodel import select

from src.api.services.base import BaseService, BaseServiceClient
from src.db.models.models import (
    AuctionQueue,
    Player,
    GullyParticipant,
    User,
    AuctionStatus,
    AuctionType,
)

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

    async def add_to_draft_squad(
        self, user_id: int, player_id: int, gully_id: int
    ) -> Dict[str, Any]:
        """Add a player to user's draft squad.

        Args:
            user_id: The ID of the user
            player_id: The ID of the player to add
            gully_id: The ID of the gully

        Returns:
            Response with success status and message
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/draft-player",
            json={"user_id": user_id, "player_id": player_id, "gully_id": gully_id},
        )
        if "error" in response:
            logger.error(f"Error adding player to draft: {response['error']}")
            return {"success": False, "message": response["error"]}
        return response

    async def remove_from_draft_squad(
        self, user_id: int, player_id: int, gully_id: int
    ) -> Dict[str, Any]:
        """Remove a player from user's draft squad.

        Args:
            user_id: The ID of the user
            player_id: The ID of the player to remove
            gully_id: The ID of the gully

        Returns:
            Response with success status and message
        """
        response = await self._make_request(
            "DELETE",
            f"{self.endpoint}/draft-player/{player_id}",
            params={"user_id": user_id, "gully_id": gully_id},
        )
        if "error" in response:
            logger.error(f"Error removing player from draft: {response['error']}")
            return {"success": False, "message": response["error"]}
        return response

    async def get_draft_squad(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Get user's draft squad.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Draft squad data including players, total price, and player count
        """
        response = await self._make_request(
            "GET",
            f"{self.endpoint}/draft-squad",
            params={"user_id": user_id, "gully_id": gully_id},
        )
        if "error" in response:
            logger.error(f"Error getting draft squad: {response['error']}")
            return {"players": [], "total_price": 0.0, "player_count": 0}
        return response

    async def submit_squad(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Submit user's final squad.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Response with success status and message
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/submit-squad",
            json={"user_id": user_id, "gully_id": gully_id},
        )
        if "error" in response:
            logger.error(f"Error submitting squad: {response['error']}")
            return {"success": False, "message": response["error"]}
        return response

    async def get_submission_status(self, gully_id: int) -> Dict[str, Any]:
        """Check submission status for a Gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            Dictionary with submission status information
        """
        # Get all participants
        stmt = select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
        result = await self.db.execute(stmt)
        participants = result.scalars().all()

        # Count submissions
        total = len(participants)
        submitted = sum(1 for p in participants if p.has_submitted_squad)

        # Get pending users
        pending_users = []
        for p in participants:
            if not p.has_submitted_squad:
                # Get user details
                user_stmt = select(User).where(User.id == p.user_id)
                user_result = await self.db.execute(user_stmt)
                user = user_result.scalars().first()

                if user:
                    pending_users.append(
                        {
                            "id": user.id,
                            "username": user.username,
                            "telegram_id": user.telegram_id,
                        }
                    )

        return {
            "all_submitted": (submitted == total),
            "total_participants": total,
            "submitted_count": submitted,
            "pending_users": pending_users,
        }

    async def start_auction(self, gully_id: int) -> Dict[str, Any]:
        """Start auction for a Gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            Dictionary with success status, message, and counts of contested/uncontested players
        """
        # Check if all users have submitted
        status = await self.get_submission_status(gully_id)

        if not status["all_submitted"]:
            return {
                "success": False,
                "message": "Not all users have submitted their squads",
            }

        # Identify contested players
        # First, get all pending players
        stmt = (
            select(AuctionQueue.player_id, func.count(AuctionQueue.id).label("count"))
            .where(
                AuctionQueue.gully_id == gully_id,
                AuctionQueue.status == AuctionStatus.PENDING.value,
            )
            .group_by(AuctionQueue.player_id)
        )

        result = await self.db.execute(stmt)
        player_counts = result.all()

        # Process each player
        contested_count = 0
        uncontested_count = 0

        for player_id, count in player_counts:
            if count > 1:
                # Contested - update status to bidding
                contested_count += 1
                update_stmt = (
                    update(AuctionQueue)
                    .where(
                        AuctionQueue.gully_id == gully_id,
                        AuctionQueue.player_id == player_id,
                        AuctionQueue.status == AuctionStatus.PENDING.value,
                    )
                    .values(status=AuctionStatus.BIDDING.value)
                )
                await self.db.execute(update_stmt)
            else:
                # Uncontested - update status to completed
                uncontested_count += 1
                update_stmt = (
                    update(AuctionQueue)
                    .where(
                        AuctionQueue.gully_id == gully_id,
                        AuctionQueue.player_id == player_id,
                        AuctionQueue.status == AuctionStatus.PENDING.value,
                    )
                    .values(status=AuctionStatus.COMPLETED.value)
                )
                await self.db.execute(update_stmt)

        await self.db.commit()

        return {
            "success": True,
            "message": "Auction started successfully",
            "contested_count": contested_count,
            "uncontested_count": uncontested_count,
        }

    async def get_contested_players(self, gully_id: int) -> Dict[str, Any]:
        """Get contested players for a Gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            Dictionary with list of contested players
        """
        stmt = select(Player).join(
            AuctionQueue,
            (AuctionQueue.player_id == Player.id)
            & (AuctionQueue.gully_id == gully_id)
            & (AuctionQueue.status == AuctionStatus.BIDDING.value),
        )
        result = await self.db.execute(stmt)
        players = result.scalars().all()

        player_list = []
        for player in players:
            player_list.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "player_type": player.player_type,
                    "base_price": (
                        float(player.base_price) if player.base_price else 0.0
                    ),
                }
            )

        return {"players": player_list}

    async def get_uncontested_players(self, gully_id: int) -> Dict[str, Any]:
        """Get uncontested players for a Gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            Dictionary with list of uncontested players
        """
        stmt = select(Player).join(
            AuctionQueue,
            (AuctionQueue.player_id == Player.id)
            & (AuctionQueue.gully_id == gully_id)
            & (AuctionQueue.status == AuctionStatus.COMPLETED.value),
        )
        result = await self.db.execute(stmt)
        players = result.scalars().all()

        player_list = []
        for player in players:
            player_list.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "player_type": player.player_type,
                    "base_price": (
                        float(player.base_price) if player.base_price else 0.0
                    ),
                }
            )

        return {"players": player_list}

    async def place_bid(
        self, user_id: int, player_id: int, gully_id: int, bid_amount: float
    ) -> Dict[str, Any]:
        """Place a bid on a contested player during auction.

        Args:
            user_id: The ID of the user placing the bid
            player_id: The ID of the player being bid on
            gully_id: The ID of the gully
            bid_amount: The amount of the bid

        Returns:
            Dictionary with success status and message
        """
        # Check if player is in bidding status
        stmt = select(AuctionQueue).where(
            AuctionQueue.gully_id == gully_id,
            AuctionQueue.player_id == player_id,
            AuctionQueue.status == AuctionStatus.BIDDING.value,
        )
        result = await self.db.execute(stmt)
        auction_item = result.scalars().first()

        if not auction_item:
            return {
                "success": False,
                "message": "Player is not available for bidding",
            }

        # Check user's remaining budget
        # This would require additional logic to calculate remaining budget

        # Record the bid
        # This would require a new model for tracking bids

        return {
            "success": True,
            "message": f"Bid of {bid_amount} Cr placed successfully",
            "user_id": user_id,
            "player_id": player_id,
            "bid_amount": bid_amount,
        }

    async def get_team_analysis(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Get analysis of a user's team.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Dictionary with team analysis data
        """
        # Get the user's team
        draft_squad = await self.get_draft_squad(user_id, gully_id)

        # Count players by role
        role_counts = {
            "batsman": 0,
            "bowler": 0,
            "all-rounder": 0,
            "wicketkeeper": 0,
        }

        # Count players by team
        team_counts = {}

        for player in draft_squad.get("players", []):
            # Count by role
            player_type = player["player_type"]
            if player_type in role_counts:
                role_counts[player_type] += 1

            # Count by team
            team = player["team"]
            if team in team_counts:
                team_counts[team] += 1
            else:
                team_counts[team] = 1

        return {
            "role_distribution": role_counts,
            "team_composition": team_counts,
            "total_players": len(draft_squad.get("players", [])),
            "total_price": draft_squad.get("total_price", 0.0),
        }


class FantasyServiceClient(BaseServiceClient):
    """Client for interacting with fantasy-related database operations."""

    async def add_to_draft_squad(
        self, user_id: int, player_id: int, gully_id: int
    ) -> Dict[str, Any]:
        """Add a player to user's draft squad.

        Args:
            user_id: The ID of the user
            player_id: The ID of the player to add
            gully_id: The ID of the gully

        Returns:
            Dictionary with success status and message
        """
        # Check if player already exists in draft
        stmt = select(AuctionQueue).where(
            AuctionQueue.gully_id == gully_id,
            AuctionQueue.player_id == player_id,
            AuctionQueue.status == AuctionStatus.DRAFT.value,
        )
        result = await self.db.execute(stmt)
        existing = result.scalars().first()

        if existing:
            # Return a dictionary with failure message
            return {"success": False, "message": "Player already in draft"}

        # Add player to auction queue with draft status
        auction_queue = AuctionQueue(
            gully_id=gully_id,
            player_id=player_id,
            auction_type=AuctionType.NEW_PLAYER.value,
            status=AuctionStatus.DRAFT.value,
        )
        self.db.add(auction_queue)
        await self.db.commit()
        await self.db.refresh(auction_queue)

        # Return a dictionary with success message
        return {"success": True, "message": "Player added to draft"}

    async def remove_from_draft_squad(
        self, user_id: int, player_id: int, gully_id: int
    ) -> Dict[str, Any]:
        """Remove a player from user's draft squad.

        Args:
            user_id: The ID of the user
            player_id: The ID of the player to remove
            gully_id: The ID of the gully

        Returns:
            Dictionary with success status and message
        """
        stmt = select(AuctionQueue).where(
            AuctionQueue.gully_id == gully_id,
            AuctionQueue.player_id == player_id,
            AuctionQueue.status == AuctionStatus.DRAFT.value,
        )
        result = await self.db.execute(stmt)
        draft_item = result.scalars().first()

        if not draft_item:
            return {"success": False, "message": "Player not found in draft"}

        await self.db.delete(draft_item)
        await self.db.commit()

        return {"success": True, "message": "Player removed from draft"}

    async def get_draft_squad(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Get user's draft squad.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Dictionary with draft squad data including players, total price, and player count
        """
        # Get all players in draft for this gully
        stmt = select(Player).join(
            AuctionQueue,
            (AuctionQueue.player_id == Player.id)
            & (AuctionQueue.gully_id == gully_id)
            & (AuctionQueue.status == AuctionStatus.DRAFT.value),
        )
        result = await self.db.execute(stmt)
        players = result.scalars().all()

        # Format response
        player_list = []
        total_price = 0.0

        for player in players:
            player_dict = {
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "player_type": player.player_type,
                "base_price": float(player.base_price) if player.base_price else 0.0,
            }
            player_list.append(player_dict)
            if player.base_price:
                total_price += float(player.base_price)

        return {
            "players": player_list,
            "total_price": total_price,
            "player_count": len(player_list),
        }

    async def submit_squad(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Submit user's final squad.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Dictionary with success status and message
        """
        # Get draft squad
        draft_squad = await self.get_draft_squad(user_id, gully_id)

        # Validate squad
        if draft_squad["player_count"] < 18:
            return {
                "success": False,
                "message": f"Squad must have 18 players. Currently has {draft_squad['player_count']}.",
            }

        if draft_squad["total_price"] > 120:
            return {
                "success": False,
                "message": f"Squad exceeds budget of 120 Cr. Current total: {draft_squad['total_price']} Cr.",
            }

        # Update all draft players to pending status
        stmt = (
            update(AuctionQueue)
            .where(
                AuctionQueue.gully_id == gully_id,
                AuctionQueue.status == AuctionStatus.DRAFT.value,
            )
            .values(status=AuctionStatus.PENDING.value)
        )
        await self.db.execute(stmt)

        # Update gully participant
        stmt = select(GullyParticipant).where(
            GullyParticipant.user_id == user_id, GullyParticipant.gully_id == gully_id
        )
        result = await self.db.execute(stmt)
        participant = result.scalars().first()

        if participant:
            participant.has_submitted_squad = True
            participant.submission_time = datetime.now(timezone.utc)
            await self.db.commit()

        return {"success": True, "message": "Squad submitted successfully"}

    async def start_auction(self, gully_id: int) -> Dict[str, Any]:
        """Start auction for a Gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            Dictionary with success status, message, and counts of contested/uncontested players
        """
        # Check if all users have submitted
        status = await self.get_submission_status(gully_id)

        if not status["all_submitted"]:
            return {
                "success": False,
                "message": "Not all users have submitted their squads",
            }

        # Identify contested players
        # First, get all pending players
        stmt = (
            select(AuctionQueue.player_id, func.count(AuctionQueue.id).label("count"))
            .where(
                AuctionQueue.gully_id == gully_id,
                AuctionQueue.status == AuctionStatus.PENDING.value,
            )
            .group_by(AuctionQueue.player_id)
        )

        result = await self.db.execute(stmt)
        player_counts = result.all()

        # Process each player
        contested_count = 0
        uncontested_count = 0

        for player_id, count in player_counts:
            if count > 1:
                # Contested - update status to bidding
                contested_count += 1
                update_stmt = (
                    update(AuctionQueue)
                    .where(
                        AuctionQueue.gully_id == gully_id,
                        AuctionQueue.player_id == player_id,
                        AuctionQueue.status == AuctionStatus.PENDING.value,
                    )
                    .values(status=AuctionStatus.BIDDING.value)
                )
                await self.db.execute(update_stmt)
            else:
                # Uncontested - update status to completed
                uncontested_count += 1
                update_stmt = (
                    update(AuctionQueue)
                    .where(
                        AuctionQueue.gully_id == gully_id,
                        AuctionQueue.player_id == player_id,
                        AuctionQueue.status == AuctionStatus.PENDING.value,
                    )
                    .values(status=AuctionStatus.COMPLETED.value)
                )
                await self.db.execute(update_stmt)

        await self.db.commit()

        return {
            "success": True,
            "message": "Auction started successfully",
            "contested_count": contested_count,
            "uncontested_count": uncontested_count,
        }

    async def get_contested_players(self, gully_id: int) -> Dict[str, Any]:
        """Get contested players for a Gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            Dictionary with list of contested players
        """
        stmt = select(Player).join(
            AuctionQueue,
            (AuctionQueue.player_id == Player.id)
            & (AuctionQueue.gully_id == gully_id)
            & (AuctionQueue.status == AuctionStatus.BIDDING.value),
        )
        result = await self.db.execute(stmt)
        players = result.scalars().all()

        player_list = []
        for player in players:
            player_list.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "player_type": player.player_type,
                    "base_price": (
                        float(player.base_price) if player.base_price else 0.0
                    ),
                }
            )

        return {"players": player_list}

    async def get_uncontested_players(self, gully_id: int) -> Dict[str, Any]:
        """Get uncontested players for a Gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            Dictionary with list of uncontested players
        """
        stmt = select(Player).join(
            AuctionQueue,
            (AuctionQueue.player_id == Player.id)
            & (AuctionQueue.gully_id == gully_id)
            & (AuctionQueue.status == AuctionStatus.COMPLETED.value),
        )
        result = await self.db.execute(stmt)
        players = result.scalars().all()

        player_list = []
        for player in players:
            player_list.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "player_type": player.player_type,
                    "base_price": (
                        float(player.base_price) if player.base_price else 0.0
                    ),
                }
            )

        return {"players": player_list}

    async def place_bid(
        self, user_id: int, player_id: int, gully_id: int, bid_amount: float
    ) -> Dict[str, Any]:
        """Place a bid on a contested player during auction.

        Args:
            user_id: The ID of the user placing the bid
            player_id: The ID of the player being bid on
            gully_id: The ID of the gully
            bid_amount: The amount of the bid

        Returns:
            Dictionary with success status and message
        """
        # Check if player is in bidding status
        stmt = select(AuctionQueue).where(
            AuctionQueue.gully_id == gully_id,
            AuctionQueue.player_id == player_id,
            AuctionQueue.status == AuctionStatus.BIDDING.value,
        )
        result = await self.db.execute(stmt)
        auction_item = result.scalars().first()

        if not auction_item:
            return {
                "success": False,
                "message": "Player is not available for bidding",
            }

        # Check user's remaining budget
        # This would require additional logic to calculate remaining budget

        # Record the bid
        # This would require a new model for tracking bids

        return {
            "success": True,
            "message": f"Bid of {bid_amount} Cr placed successfully",
            "user_id": user_id,
            "player_id": player_id,
            "bid_amount": bid_amount,
        }

    async def get_team_analysis(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Get analysis of a user's team.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Dictionary with team analysis data
        """
        # Get the user's team
        draft_squad = await self.get_draft_squad(user_id, gully_id)

        # Count players by role
        role_counts = {
            "batsman": 0,
            "bowler": 0,
            "all-rounder": 0,
            "wicketkeeper": 0,
        }

        # Count players by team
        team_counts = {}

        for player in draft_squad.get("players", []):
            # Count by role
            player_type = player["player_type"]
            if player_type in role_counts:
                role_counts[player_type] += 1

            # Count by team
            team = player["team"]
            if team in team_counts:
                team_counts[team] += 1
            else:
                team_counts[team] = 1

        return {
            "role_distribution": role_counts,
            "team_composition": team_counts,
            "total_players": len(draft_squad.get("players", [])),
            "total_price": draft_squad.get("total_price", 0.0),
        }
