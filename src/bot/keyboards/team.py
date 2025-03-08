"""
Keyboard utilities for team management.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List


def get_team_management_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboard for team management."""
    keyboard = [
        [
            InlineKeyboardButton("Set Captain", callback_data="team_set_captain"),
            InlineKeyboardButton("View Players", callback_data="team_view_players"),
        ],
        [
            InlineKeyboardButton(
                "Check Composition", callback_data="team_check_composition"
            ),
            InlineKeyboardButton("Transfer", callback_data="team_transfer"),
        ],
        [InlineKeyboardButton("Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_captain_selection_keyboard(
    players: List[Dict[str, Any]], page: int = 0, items_per_page: int = 5
) -> InlineKeyboardMarkup:
    """Create a keyboard for captain selection."""
    # Calculate pagination
    total_pages = (len(players) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(players))

    # Create player buttons
    keyboard = []
    for i in range(start_idx, end_idx):
        player = players[i]
        player_id = player.get("id")
        player_name = player.get("name", "Unknown")
        player_type = player.get("type", "Unknown")

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{player_name} ({player_type})",
                    callback_data=f"captain_select_{player_id}",
                )
            ]
        )

    # Add navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton("◀️ Previous", callback_data=f"captain_page_{page-1}")
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"captain_page_{page+1}")
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    # Add cancel button
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="team_cancel")])

    return InlineKeyboardMarkup(keyboard)
