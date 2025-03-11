"""
Utility functions for creating mock data for tests
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from decimal import Decimal

from src.tests.utils.mock_models import (
    MockUser,
    MockGully,
    MockGullyParticipant,
    MockPlayer,
    MockUserPlayer,
)


class MockDataFactory:
    @staticmethod
    def user(
        id: int = 1,
        telegram_id: int = 12345678,
        username: str = "test_user",
        full_name: str = "Test User",
    ) -> Dict[str, Any]:
        return {
            "id": id,
            "telegram_id": telegram_id,
            "username": username,
            "full_name": full_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def mock_user(
        id: int = 1,
        telegram_id: int = 12345678,
        username: str = "test_user",
        full_name: str = "Test User",
    ) -> MockUser:
        return MockUser(
            id=id,
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )

    @staticmethod
    def gully(
        id: int = 1,
        name: str = "Test Gully",
        telegram_group_id: int = 87654321,
    ) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "telegram_group_id": telegram_group_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def mock_gully(
        id: int = 1,
        name: str = "Test Gully",
        telegram_group_id: int = 87654321,
    ) -> MockGully:
        return MockGully(
            id=id,
            name=name,
            telegram_group_id=telegram_group_id,
        )

    @staticmethod
    def gully_participant(
        id: int = 1,
        user_id: int = 1,
        gully_id: int = 1,
        team_name: str = "Test Team",
        budget: float = 120.0,
        points: int = 0,
        role: str = "member",
    ) -> Dict[str, Any]:
        return {
            "id": id,
            "user_id": user_id,
            "gully_id": gully_id,
            "team_name": team_name,
            "budget": budget,
            "points": points,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def mock_gully_participant(
        id: int = 1,
        user_id: int = 1,
        gully_id: int = 1,
        team_name: str = "Test Team",
        budget: float = 120.0,
        points: int = 0,
        role: str = "member",
    ) -> MockGullyParticipant:
        return MockGullyParticipant(
            id=id,
            user_id=user_id,
            gully_id=gully_id,
            team_name=team_name,
            budget=Decimal(str(budget)),
            points=points,
            role=role,
        )

    @staticmethod
    def player(
        id: int = 1,
        name: str = "Virat Kohli",
        team: str = "RCB",
        player_type: str = "BAT",
        base_price: float = 20.0,
        sold_price: Optional[float] = 25.0,
        season: int = 2025,
    ) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "team": team,
            "player_type": player_type,
            "base_price": base_price,
            "sold_price": sold_price,
            "season": season,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def mock_player(
        id: int = 1,
        name: str = "Virat Kohli",
        team: str = "RCB",
        player_type: str = "BAT",
        base_price: float = 20.0,
        sold_price: Optional[float] = 25.0,
        season: int = 2025,
    ) -> MockPlayer:
        return MockPlayer(
            id=id,
            name=name,
            team=team,
            player_type=player_type,
            base_price=Decimal(str(base_price)) if base_price is not None else None,
            sold_price=Decimal(str(sold_price)) if sold_price is not None else None,
            season=season,
        )

    @staticmethod
    def user_player(
        id: int = 1,
        user_id: int = 1,
        player_id: int = 1,
        gully_id: int = 1,
        purchase_price: float = 25.0,
        is_captain: bool = False,
        is_vice_captain: bool = False,
        is_playing_xi: bool = True,
    ) -> Dict[str, Any]:
        return {
            "id": id,
            "user_id": user_id,
            "player_id": player_id,
            "gully_id": gully_id,
            "purchase_price": purchase_price,
            "is_captain": is_captain,
            "is_vice_captain": is_vice_captain,
            "is_playing_xi": is_playing_xi,
            "purchase_date": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def mock_user_player(
        id: int = 1,
        user_id: int = 1,
        player_id: int = 1,
        gully_id: int = 1,
        purchase_price: float = 25.0,
        is_captain: bool = False,
        is_vice_captain: bool = False,
        is_playing_xi: bool = True,
    ) -> MockUserPlayer:
        return MockUserPlayer(
            id=id,
            user_id=user_id,
            player_id=player_id,
            gully_id=gully_id,
            purchase_price=Decimal(str(purchase_price)),
            is_captain=is_captain,
            is_vice_captain=is_vice_captain,
            is_playing_xi=is_playing_xi,
        )

    @staticmethod
    def match(
        id: int = 1,
        date: str = "2025-04-10",
        venue: str = "M. Chinnaswamy Stadium",
        team1: str = "RCB",
        team2: str = "MI",
        team1_score: Optional[str] = "200/3",
        team2_score: Optional[str] = "180/8",
        match_winner: Optional[str] = "RCB",
    ) -> Dict[str, Any]:
        return {
            "id": id,
            "date": date,
            "venue": venue,
            "team1": team1,
            "team2": team2,
            "team1_score": team1_score,
            "team2_score": team2_score,
            "match_winner": match_winner,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
