"""
Factory classes for creating fantasy-related response objects.
"""

from typing import Dict, Any, List, Union
from src.api.schemas.player import PlayerType
from src.api.schemas.auction import AuctionStartResponse


class PlayerResponseFactory:
    """Factory for creating player response objects within draft selections."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a player response from data.

        Args:
            data: Player data

        Returns:
            Player response
        """
        # Ensure player_type is a valid enum value
        player_type = data.get("player_type")

        # If player_type is a string, try to convert it to the enum value
        if isinstance(player_type, str):
            # Check if the string matches any of the enum values
            try:
                player_type = PlayerType(player_type)
            except ValueError:
                # If conversion fails, use a default value
                player_type = PlayerType.BAT

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "team": data.get("team"),
            "player_type": player_type,
            "base_price": data.get("base_price"),
            "sold_price": data.get("sold_price"),
            "season": data.get("season"),
        }


class DraftPlayerResponseFactory:
    """Factory for creating draft player response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a draft player response from data.

        Args:
            data: Draft player data

        Returns:
            Draft player response
        """
        return {
            "id": data.get("id"),
            "player_id": data.get("player_id"),
            "participant_id": data.get("participant_id"),
            "selected_at": data.get("selected_at"),
            "status": data.get("status"),
            "player": (
                PlayerResponseFactory.create_response(data.get("player", {}))
                if data.get("player")
                else None
            ),
        }


class DraftSelectionResponseFactory:
    """Factory for creating draft selection response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a draft selection response from data.

        Args:
            data: Draft selection data

        Returns:
            Draft selection response
        """
        # Ensure player_type is a valid enum value
        player_type = data.get("player_type")

        # If player_type is a string, try to convert it to the enum value
        if isinstance(player_type, str):
            # Check if the string matches any of the enum values
            try:
                player_type = PlayerType(player_type)
            except ValueError:
                # If conversion fails, use a default value
                player_type = PlayerType.BAT

        return {
            "id": data.get("draft_selection_id"),
            "player_id": data.get("id"),  # This is the player's ID
            "name": data.get("name"),
            "team": data.get("team"),
            "player_type": player_type,
            "base_price": data.get("base_price"),
            "sold_price": data.get("sold_price"),
            "season": data.get("season"),
            "selected_at": data.get("selected_at"),
        }

    @staticmethod
    def create_response_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a list of draft selection responses from data.

        Args:
            data_list: List of draft selection data

        Returns:
            List of draft selection responses
        """
        return [
            DraftSelectionResponseFactory.create_response(data) for data in data_list
        ]


class SquadResponseFactory:
    """Factory for creating squad response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a squad response from data.

        Args:
            data: Squad data

        Returns:
            Squad response
        """
        return {
            "players": [
                DraftSelectionResponseFactory.create_response(player)
                for player in data.get("players", [])
            ],
            "player_count": len(data.get("players", [])),
        }


class BulkDraftPlayerResponseFactory:
    """Factory for creating bulk draft player operation response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a bulk draft player operation response from data.

        Args:
            data: Bulk operation result data

        Returns:
            Bulk operation response
        """
        return {
            "success": data.get("success", False),
            "message": data.get("message", ""),
            "added_count": data.get("added_count", 0),
            "removed_count": data.get("removed_count", 0),
            "failed_ids": data.get("failed_ids", []),
        }


class SubmissionStatusResponseFactory:
    """Factory for creating submission status response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a submission status response from data.

        Args:
            data: Submission status data

        Returns:
            Submission status response
        """
        return {
            "gully_id": data.get("gully_id"),
            "gully_status": data.get("gully_status"),
            "total_participants": data.get("total_participants", 0),
            "submitted_participants": data.get("submitted_participants", 0),
            "all_submitted": data.get("all_submitted", False),
            "submitted_details": data.get("submitted_details", []),
            "not_submitted_details": data.get("not_submitted_details", []),
        }


class AuctionStartResponseFactory:
    """Factory for creating auction start response objects."""

    @staticmethod
    def create_response(
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
            data_dict = data.model_dump()
        else:
            data_dict = data

        return {
            "success": True,
            "message": "Auction started successfully",
            "data": {
                "gully_id": data_dict.get("gully_id"),
                "status": data_dict.get("status"),
                "contested_players_count": data_dict.get("contested_count"),
                "uncontested_players_count": data_dict.get("uncontested_count"),
                "contested_players": data_dict.get("contested_players"),
                "uncontested_players": data_dict.get("uncontested_players"),
            },
        }


class ContestPlayerResponseFactory:
    """Factory for creating contest player response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a contest player response from data.

        Args:
            data: Contest player data

        Returns:
            Contest player response
        """
        # Ensure player_type is a valid enum value
        player_type = data.get("player_type")

        # If player_type is a string, try to convert it to the enum value
        if isinstance(player_type, str):
            # Check if the string matches any of the enum values
            try:
                player_type = PlayerType(player_type)
            except ValueError:
                # If conversion fails, use a default value
                player_type = PlayerType.BAT

        return {
            "player_id": data.get("player_id"),
            "name": data.get("name"),
            "team": data.get("team"),
            "player_type": player_type,
            "base_price": data.get("base_price"),
            "contested_by": data.get("contested_by", []),
            "contest_count": len(data.get("contested_by", [])),
        }


class FinalizeDraftResponseFactory:
    """Factory for creating finalize draft response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a finalize draft response from data.

        Args:
            data: Finalize draft data

        Returns:
            Finalize draft response
        """
        return {
            "gully_id": data.get("gully_id"),
            "status": data.get("status"),
            "message": data.get("message"),
            "success": data.get("success", False),
        }
