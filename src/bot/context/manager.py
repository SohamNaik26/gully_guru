"""
Context manager for the GullyGuru bot.
Handles storing and retrieving data from the Telegram context.
"""

import logging
from typing import Dict, Any, List, Optional
from telegram.ext import ContextTypes

# Configure logging
logger = logging.getLogger(__name__)

# Context keys
USER_ID = "user_id"
ACTIVE_GULLY_ID = "active_gully_id"
SELECTED_PLAYER_IDS = "selected_player_ids"
CURRENT_SQUAD = "current_squad"
PARTICIPANT_ID = "participant_id"
TEAM_NAME = "team_name"


def get_user_id(context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Get the user ID from context."""
    return context.user_data.get(USER_ID)


def set_user_id(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Set the user ID in context."""
    context.user_data[USER_ID] = user_id
    logger.debug(f"Set user_id in context: {user_id}")


def get_active_gully_id(context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Get the active gully ID from context."""
    return context.user_data.get(ACTIVE_GULLY_ID)


def set_active_gully_id(context: ContextTypes.DEFAULT_TYPE, gully_id: int) -> None:
    """Set the active gully ID in context."""
    context.user_data[ACTIVE_GULLY_ID] = gully_id
    logger.debug(f"Set active_gully_id in context: {gully_id}")


def get_participant_id(context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Get the participant ID from context."""
    return context.user_data.get(PARTICIPANT_ID)


def set_participant_id(context: ContextTypes.DEFAULT_TYPE, participant_id: int) -> None:
    """Set the participant ID in context."""
    context.user_data[PARTICIPANT_ID] = participant_id
    logger.debug(f"Set participant_id in context: {participant_id}")


def get_team_name(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Get the team name from context."""
    return context.user_data.get(TEAM_NAME)


def set_team_name(context: ContextTypes.DEFAULT_TYPE, team_name: str) -> None:
    """Set the team name in context."""
    context.user_data[TEAM_NAME] = team_name
    logger.debug(f"Set team_name in context: {team_name}")


def get_selected_player_ids(context: ContextTypes.DEFAULT_TYPE) -> List[int]:
    """Get the selected player IDs from context."""
    return context.user_data.get(SELECTED_PLAYER_IDS, [])


def set_selected_player_ids(
    context: ContextTypes.DEFAULT_TYPE, player_ids: List[int]
) -> None:
    """Set the selected player IDs in context."""
    context.user_data[SELECTED_PLAYER_IDS] = player_ids
    logger.debug(f"Set selected_player_ids in context: {player_ids}")


def add_selected_player_id(context: ContextTypes.DEFAULT_TYPE, player_id: int) -> None:
    """Add a player ID to the selected players list."""
    player_ids = get_selected_player_ids(context)
    if player_id not in player_ids:
        player_ids.append(player_id)
        set_selected_player_ids(context, player_ids)
        logger.debug(f"Added player_id {player_id} to selected_player_ids")


def remove_selected_player_id(
    context: ContextTypes.DEFAULT_TYPE, player_id: int
) -> None:
    """Remove a player ID from the selected players list."""
    player_ids = get_selected_player_ids(context)
    if player_id in player_ids:
        player_ids.remove(player_id)
        set_selected_player_ids(context, player_ids)
        logger.debug(f"Removed player_id {player_id} from selected_player_ids")


def toggle_selected_player_id(
    context: ContextTypes.DEFAULT_TYPE, player_id: int
) -> bool:
    """
    Toggle a player ID in the selected players list.

    Returns:
        bool: True if player was added, False if removed
    """
    player_ids = get_selected_player_ids(context)
    if player_id in player_ids:
        player_ids.remove(player_id)
        set_selected_player_ids(context, player_ids)
        logger.debug(f"Toggled OFF player_id {player_id}")
        return False
    else:
        player_ids.append(player_id)
        set_selected_player_ids(context, player_ids)
        logger.debug(f"Toggled ON player_id {player_id}")
        return True


def get_current_squad(context: ContextTypes.DEFAULT_TYPE) -> List[Dict[str, Any]]:
    """Get the current squad from context."""
    return context.user_data.get(CURRENT_SQUAD, [])


def set_current_squad(
    context: ContextTypes.DEFAULT_TYPE, squad: List[Dict[str, Any]]
) -> None:
    """Set the current squad in context."""
    context.user_data[CURRENT_SQUAD] = squad
    logger.debug(f"Set current_squad in context with {len(squad)} players")


def clear_squad_selection(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all squad selection data from context."""
    if SELECTED_PLAYER_IDS in context.user_data:
        del context.user_data[SELECTED_PLAYER_IDS]
    if CURRENT_SQUAD in context.user_data:
        del context.user_data[CURRENT_SQUAD]
    logger.debug("Cleared squad selection data from context")


def clear_context(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all context data."""
    context.user_data.clear()
    logger.debug("Cleared all context data")
