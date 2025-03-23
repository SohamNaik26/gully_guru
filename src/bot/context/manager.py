"""
Context manager for GullyGuru bot.
Manages user and gully-specific data within the telegram bot context.
"""

import logging
from typing import Any, Dict, List, Optional
import time

# Configure logging
logger = logging.getLogger(__name__)

"""
Sample data structure for user_data and bot_data:

user_data = {
    # Global user data
    "user_id": 123456789,  # User's database ID
    "active_gully_id": 7,  # Currently selected gully
    
    # Gully-specific user data
    "gullies": {
        7: {  # Gully ID
            "participant_id": 42,  # User's participant ID in this gully
            "team_name": "Super XI",  # User's team name in this gully
            
            # Squad management
            "current_squad": [
                {"id": 101, "name": "Player 1", "role": "BATSMAN", ...},
                {"id": 102, "name": "Player 2", "role": "BOWLER", ...},
                # More players...
            ],
            "selected_player_ids": [101, 102, 103],  # Player IDs selected in UI
            
            # Release management
            "release_player_ids": [104, 105],  # Player IDs selected for release
            "release_submitted": True,  # Whether user has submitted releases
        },
        # More gullies...
    }
}

bot_data = {
    # Cached gully data
    "gully_data": {
        7: {
            "id": 7,
            "name": "Test Gully",
            "status": "auction",
            "telegram_group_id": -1001234567890,
            "_cache_timestamp": 1616161616.0,
            # Other gully data...
        },
        # More gullies...
    },
    
    # Gully-specific bot data
    "gullies": {
        7: {  # Gully ID
            # Auction state
            "release_window_open": True,  # Whether release window is open
            "auction_start_time": 1616161616.0,  # When auction started
            "auction_paused": False,  # Whether auction is paused
            
            # Cached player data
            "uncontested_players": [
                {"player_id": 101, "player_name": "Player 1", "team": "Team A", ...},
                {"player_id": 102, "player_name": "Player 2", "team": "Team B", ...},
                # More players...
            ],
            "contested_players": [
                {"player_id": 201, "name": "Player X", "team": "Team C", ...},
                # More players...
            ],
        },
        # More gullies...
    }
}
"""

# Helper functions for working with context


def ensure_user_gully_data(context, gully_id):
    """Ensure user gully data exists in context."""
    if "gullies" not in context.user_data:
        context.user_data["gullies"] = {}
    if gully_id not in context.user_data["gullies"]:
        context.user_data["gullies"][gully_id] = {}
    return context.user_data["gullies"][gully_id]


def ensure_bot_gully_data(context, gully_id):
    """Ensure bot gully data exists in context."""
    if "gullies" not in context.bot_data:
        context.bot_data["gullies"] = {}
    if gully_id not in context.bot_data["gullies"]:
        context.bot_data["gullies"][gully_id] = {}
    return context.bot_data["gullies"][gully_id]


# User ID management (global to the user)


def set_user_id(context, user_id):
    """Set user ID in context."""
    context.user_data["user_id"] = user_id
    logger.info(f"Setting user_id: {user_id}")


def get_user_id(context):
    """Get user ID from context."""
    return context.user_data.get("user_id")


# Active gully management


def set_active_gully_id(context, gully_id):
    """Set active gully ID for this user."""
    context.user_data["active_gully_id"] = gully_id
    logger.info(f"Setting active_gully_id: {gully_id}")


def get_active_gully_id(context, chat_id=None):
    """
    Get active gully ID for a chat.
    If chat_id is provided, look for that specific chat.
    Otherwise, try to get from message chat_id.
    """
    if chat_id:
        # If chat_id is provided, use that to find the gully
        all_gullies = context.bot_data.get("gullies", {})
        for g_id, gully_data in all_gullies.items():
            if gully_data.get("telegram_group_id") == chat_id:
                return g_id
    
    # Otherwise use the active_gully_id from chat_data if available
    return context.chat_data.get("active_gully_id")


# Participant management


def set_participant_id(context, participant_id, gully_id):
    """Set participant ID for specific gully."""
    user_gully_data = ensure_user_gully_data(context, gully_id)
    user_gully_data["participant_id"] = participant_id
    logger.info(f"Setting participant_id: {participant_id} for gully: {gully_id}")


def get_participant_id(context, gully_id=None):
    """Get participant ID for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return None

    gully_data = context.user_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("participant_id")


# Team name management


def set_team_name(context, team_name, gully_id):
    """Set team name for specific gully."""
    user_gully_data = ensure_user_gully_data(context, gully_id)
    user_gully_data["team_name"] = team_name
    logger.info(f"Setting team_name: {team_name} for gully: {gully_id}")


def get_team_name(context, gully_id=None):
    """Get team name for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return None

    gully_data = context.user_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("team_name")


# Squad management


def set_current_squad(context, squad, gully_id):
    """Set current squad for specific gully."""
    user_gully_data = ensure_user_gully_data(context, gully_id)
    user_gully_data["current_squad"] = squad
    logger.info(
        f"Setting current squad with {len(squad)} players for gully: {gully_id}"
    )


def get_current_squad(context, gully_id=None):
    """Get current squad for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return []

    gully_data = context.user_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("current_squad", [])


def set_selected_player_ids(context, player_ids, gully_id):
    """Set selected player IDs for specific gully."""
    user_gully_data = ensure_user_gully_data(context, gully_id)
    user_gully_data["selected_player_ids"] = player_ids
    logger.info(f"Setting {len(player_ids)} selected player IDs for gully: {gully_id}")


def get_selected_player_ids(context, gully_id=None):
    """Get selected player IDs for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return []

    gully_data = context.user_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("selected_player_ids", [])


def toggle_selected_player_id(context, player_id, gully_id):
    """Toggle player ID in selected players for specific gully."""
    selected_ids = get_selected_player_ids(context, gully_id)
    if player_id in selected_ids:
        selected_ids.remove(player_id)
        logger.info(f"Removed player {player_id} from selection for gully: {gully_id}")
    else:
        selected_ids.append(player_id)
        logger.info(f"Added player {player_id} to selection for gully: {gully_id}")

    set_selected_player_ids(context, selected_ids, gully_id)
    return selected_ids


def clear_squad_selection(context, gully_id):
    """Clear squad selection for specific gully."""
    user_gully_data = ensure_user_gully_data(context, gully_id)
    if "selected_player_ids" in user_gully_data:
        del user_gully_data["selected_player_ids"]
    if "current_squad" in user_gully_data:
        del user_gully_data["current_squad"]
    logger.info(f"Cleared squad selection for gully: {gully_id}")


# Release player management


def set_selected_release_player_ids(context, player_ids, gully_id):
    """Set selected player IDs for release in specific gully."""
    user_gully_data = ensure_user_gully_data(context, gully_id)
    user_gully_data["release_player_ids"] = player_ids
    logger.info(f"Setting {len(player_ids)} release player IDs for gully: {gully_id}")


def get_selected_release_player_ids(context, gully_id=None):
    """Get selected player IDs for release in specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return []

    gully_data = context.user_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("release_player_ids", [])


def set_release_submitted(context, submitted, gully_id):
    """Set release submitted status for specific gully."""
    user_gully_data = ensure_user_gully_data(context, gully_id)
    user_gully_data["release_submitted"] = submitted
    logger.info(f"Setting release_submitted: {submitted} for gully: {gully_id}")


def is_release_submitted(context, gully_id=None):
    """Check if release is submitted for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return False

    gully_data = context.user_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("release_submitted", False)


# Global gully state management


def set_release_window_state(context, gully_id, is_open):
    """Set release window state for specific gully."""
    bot_gully_data = ensure_bot_gully_data(context, gully_id)
    bot_gully_data["release_window_open"] = is_open
    logger.info(f"Setting release_window_open: {is_open} for gully: {gully_id}")


def is_release_window_open(context, gully_id=None):
    """Check if release window is open for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return False

    gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("release_window_open", False)


def set_auction_start_time(context, gully_id, start_time):
    """Set auction start time for specific gully."""
    bot_gully_data = ensure_bot_gully_data(context, gully_id)
    bot_gully_data["auction_start_time"] = start_time
    logger.info(f"Setting auction_start_time: {start_time} for gully: {gully_id}")


def get_auction_start_time(context, gully_id=None):
    """Get auction start time for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return None

    gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("auction_start_time")


def set_auction_paused(context, paused, gully_id):
    """Set auction paused state for specific gully."""
    bot_gully_data = ensure_bot_gully_data(context, gully_id)
    bot_gully_data["auction_paused"] = paused
    logger.info(f"Setting auction_paused: {paused} for gully: {gully_id}")


def is_auction_paused(context, gully_id=None):
    """Check if auction is paused for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return False

    gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("auction_paused", False)


# Auction player management


def set_uncontested_players(context, gully_id, players):
    """Store uncontested players for specific gully."""
    bot_gully_data = ensure_bot_gully_data(context, gully_id)
    bot_gully_data["uncontested_players"] = players
    logger.info(f"Storing {len(players)} uncontested players for gully: {gully_id}")


def get_uncontested_players(context, gully_id=None):
    """Get uncontested players for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return []

    gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("uncontested_players", [])


def set_contested_players(context, gully_id, players):
    """Store contested players for specific gully."""
    bot_gully_data = ensure_bot_gully_data(context, gully_id)
    bot_gully_data["contested_players"] = players
    logger.info(f"Storing {len(players)} contested players for gully: {gully_id}")


def get_contested_players(context, gully_id=None):
    """Get contested players for specific gully."""
    if gully_id is None:
        gully_id = get_active_gully_id(context)
        if gully_id is None:
            return []

    gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("contested_players", [])


def update_gully_data(context, gully_id, gully_data):
    """Update gully data in context with fresh information and timestamp."""
    bot_gully_data = ensure_bot_gully_data(context, gully_id)
    bot_gully_data.update(gully_data)
    bot_gully_data["_cache_timestamp"] = time.time()
    logger.info(
        f"Updated gully data for gully: {gully_id}, status: {gully_data.get('status')}"
    )


def is_gully_cache_fresh(context, gully_id, max_age_seconds=60):
    """Check if cached gully data is fresh enough."""
    if (
        "gully_data" not in context.bot_data
        or gully_id not in context.bot_data["gully_data"]
    ):
        return False

    gully_data = context.bot_data["gully_data"][gully_id]
    timestamp = gully_data.get("_cache_timestamp", 0)
    return (time.time() - timestamp) < max_age_seconds


async def get_gully_with_fresh_check(context, gully_id, max_age_seconds=60):
    """Get gully data, refreshing from API if cache is stale."""
    if not is_gully_cache_fresh(context, gully_id, max_age_seconds):
        # Import inside function to avoid circular imports
        from src.bot.api_client.init import get_initialized_onboarding_client

        client = await get_initialized_onboarding_client()
        return await client.get_gully(gully_id, context)

    return context.bot_data.get("gully_data", {}).get(gully_id)


def clear_gully_cache(context, gully_id=None):
    """Clear cached gully data."""
    if gully_id is None:
        # Clear all gully cache
        if "gully_data" in context.bot_data:
            del context.bot_data["gully_data"]
        logger.info("Cleared all gully cache")
    else:
        # Clear specific gully cache
        if (
            "gully_data" in context.bot_data
            and gully_id in context.bot_data["gully_data"]
        ):
            del context.bot_data["gully_data"][gully_id]
            logger.info(f"Cleared cache for gully: {gully_id}")
