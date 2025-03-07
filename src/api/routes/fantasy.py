from typing import Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.bot.utils.auction import validate_team_composition
from src.models.user import User
from src.models.player import Player
from src.models.user_player_link import UserPlayerLink
from src.database.session import get_session

router = APIRouter()


@router.post("/validate-team", response_model=Dict[str, Any])
async def validate_user_team(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Validate a user's team composition."""
    # Check if user exists
    user = session.exec(select(User).where(User.id == user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get user's team
    user_players = session.exec(
        select(Player).join(UserPlayerLink).where(UserPlayerLink.user_id == user_id)
    ).all()

    # Convert to list of dicts for validation
    players = [
        {
            "id": player.id,
            "name": player.name,
            "team": player.team,
            "player_type": player.player_type,
        }
        for player in user_players
    ]

    # Validate team composition
    validation_result = validate_team_composition(players)

    # Count players by role
    role_counts = {"BAT": 0, "BOWL": 0, "ALL": 0, "WK": 0}

    for player in players:
        player_type = player.get("player_type", "")
        if player_type in role_counts:
            role_counts[player_type] += 1

    # Add role counts to result
    validation_result["role_counts"] = role_counts
    validation_result["total_players"] = len(players)

    return validation_result
