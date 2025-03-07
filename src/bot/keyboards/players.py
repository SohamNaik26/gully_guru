from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List


def get_player_filters_keyboard():
    """Create a keyboard for player filters."""
    teams = ["MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"]
    player_types = ["BAT", "BOWL", "ALL", "WK"]

    keyboard = []

    # Team filters
    team_row1 = []
    team_row2 = []

    for i, team in enumerate(teams[:5]):
        team_row1.append(
            InlineKeyboardButton(team, callback_data=f"player_filter_team_{team}")
        )

    for i, team in enumerate(teams[5:]):
        team_row2.append(
            InlineKeyboardButton(team, callback_data=f"player_filter_team_{team}")
        )

    keyboard.append(team_row1)
    keyboard.append(team_row2)

    # Player type filters
    type_row = []
    for player_type in player_types:
        type_row.append(
            InlineKeyboardButton(
                player_type, callback_data=f"player_filter_type_{player_type}"
            )
        )

    keyboard.append(type_row)

    # Clear filters and back buttons
    keyboard.append(
        [
            InlineKeyboardButton("Clear Filters", callback_data="player_filter_clear"),
            InlineKeyboardButton("« Back", callback_data="nav_back_players"),
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def get_player_details_keyboard(player: Dict[str, Any]):
    """Create a keyboard for player details."""
    keyboard = []

    # Add to team button (if not already in team)
    if not player.get("in_user_team", False):
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Add to Team", callback_data=f"player_add_{player['id']}"
                )
            ]
        )
    else:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Remove from Team", callback_data=f"player_remove_{player['id']}"
                )
            ]
        )

    # Bid button (if auction is active)
    if player.get("auction_status") == "active":
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Place Bid", callback_data=f"auction_bid_{player['id']}"
                )
            ]
        )

    # Set as captain button (if in team)
    if player.get("in_user_team", False):
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Set as Captain", callback_data=f"player_captain_{player['id']}"
                )
            ]
        )

    # Back button
    keyboard.append(
        [InlineKeyboardButton("« Back to Players", callback_data="nav_back_players")]
    )

    return InlineKeyboardMarkup(keyboard)
