"""
Factory for creating auction-related responses.
"""

from typing import Dict, Any, List, Union
from src.api.schemas.auction import (
    AuctionStartResponse,
    AuctionQueueResponse,
)


class AuctionResponseFactory:
    """Factory for creating auction-related responses."""

    @staticmethod
    def create_start_auction_response(
        data: Union[Dict[str, Any], AuctionStartResponse],
    ) -> Dict[str, Any]:
        """
        Create a response for auction start.

        Args:
            data: Auction start data or AuctionStartResponse object

        Returns:
            Response data
        """
        # Convert Pydantic model to dict if needed
        if isinstance(data, AuctionStartResponse):
            data_dict = (
                data.model_dump() if hasattr(data, "model_dump") else data.dict()
            )
        else:
            data_dict = data

        return {
            "success": True,
            "message": data_dict.get("message", "Auction started successfully"),
            "data": {
                "gully_id": data_dict.get("gully_id"),
                "status": data_dict.get("status"),
                "contested_count": data_dict.get("contested_count"),
                "uncontested_count": data_dict.get("uncontested_count"),
                "contested_players": data_dict.get("contested_players"),
                "uncontested_players": data_dict.get("uncontested_players"),
            },
        }

    @staticmethod
    def create_stop_auction_response(
        gully_id: int,
        success: bool = True,
        message: str = "Auction stopped successfully",
    ) -> Dict[str, Any]:
        """
        Create a response for auction stop.

        Args:
            gully_id: Gully ID
            success: Whether the operation was successful
            message: Response message

        Returns:
            Response data
        """
        return {
            "success": success,
            "message": message,
            "data": {"gully_id": gully_id, "status": "stopped"},
        }

    @staticmethod
    def create_auction_queue_response(
        players: List[AuctionQueueResponse],
        gully_id: int,
    ) -> Dict[str, Any]:
        """
        Create a response for auction queue.
        """
        return {
            "success": True,
            "message": "Auction queue retrieved successfully",
            "data": {
                "gully_id": gully_id,
                "players": players,
                "total_players": len(players),
            },
        }

    @staticmethod
    def create_release_players_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a response for releasing players.

        Args:
            data: Release players data

        Returns:
            Response data
        """
        return {
            "success": True,
            "message": data.get("message", "Players released successfully"),
            "data": {
                "released_count": data.get("released_count", 0),
                "released_players": data.get("released_players", []),
            },
        }

    @staticmethod
    def create_players_by_participant_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a response for players grouped by participant.

        Args:
            data: Players by participant data

        Returns:
            Response data
        """
        return {
            "success": True,
            "message": f"Retrieved players for gully {data.get('gully_id')}",
            "data": {
                "gully_id": data.get("gully_id"),
                "gully_name": data.get("gully_name"),
                "gully_status": data.get("gully_status"),
                "participants": data.get("participants", []),
                "total_players": data.get("total_players", 0),
            },
        }

    @staticmethod
    def create_next_player_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a response for next player request.

        Args:
            data: Next player data

        Returns:
            Response data
        """
        return {
            "success": True,
            "message": "Next player in auction queue",
            "data": {
                "player": data.get("player"),
                "participants": data.get("participants", []),
            },
        }

    @staticmethod
    def create_resolve_contested_player_response(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a response for resolving contested player.

        Args:
            data: Resolution data

        Returns:
            Response data
        """
        return {
            "success": True,
            "message": data.get("message", "Player successfully assigned."),
            "data": {
                "status": data.get("status", "success"),
                "auction_queue_id": data.get("auction_queue_id"),
                "player_id": data.get("player_id"),
                "player_name": data.get("player_name"),
                "winning_participant_id": data.get("winning_participant_id"),
                "winning_team_name": data.get("winning_team_name"),
            },
        }

    @staticmethod
    def create_revert_auction_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a response for auction reversion.

        Args:
            data: Reversion data

        Returns:
            Response data
        """
        return {
            "success": True,
            "message": data.get("message", "Auction result reverted"),
            "data": {
                "auction_queue_id": data.get("auction_queue_id"),
                "status": data.get("status", "success"),
            },
        }
