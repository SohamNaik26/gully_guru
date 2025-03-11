from typing import Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.api.dependencies import get_current_user
from src.db.models.models import User
from src.db.models.models import Player
from src.db.models.models import UserPlayer
from src.db.session import get_session

router = APIRouter()


# Add placeholder function for team validation
def validate_team_composition(team_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate team composition according to fantasy cricket rules.

    Args:
        team_data: Dictionary containing team data

    Returns:
        Dictionary with validation results
    """
    # TODO: Implement team validation logic
    return {"valid": True, "message": "Team composition is valid"}


@router.post("/validate-team", response_model=Dict[str, Any])
async def validate_user_team(
    user_id: int,
    gully_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Validate a user's team composition within a specific gully."""
    # Check if user exists
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get user's team in the specific gully
    result = await session.execute(
        select(Player)
        .join(UserPlayer)
        .where(UserPlayer.user_id == user_id, UserPlayer.gully_id == gully_id)
    )
    user_players = result.scalars().all()

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
