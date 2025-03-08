from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List, Optional


def get_gully_management_keyboard(gully_id: int):
    """Create a keyboard for gully management."""
    keyboard = [
        [
            InlineKeyboardButton("Join Gully", callback_data=f"gully_join_{gully_id}"),
            InlineKeyboardButton(
                "View Leaderboard", callback_data=f"gully_leaderboard_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Start Auction", callback_data=f"gully_start_auction_{gully_id}"
            ),
            InlineKeyboardButton(
                "Open Transfers", callback_data=f"gully_open_transfers_{gully_id}"
            ),
        ],
        [InlineKeyboardButton("« Back to Gullies", callback_data="nav_my_gullies")],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_gully_list_keyboard(gullies: List[Dict[str, Any]], action: str = "switch"):
    """Create a keyboard for gully list."""
    keyboard = []

    for gully in gullies:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{gully.get('name')} ({gully.get('status')})",
                    callback_data=f"{action}_gully_{gully.get('id')}",
                )
            ]
        )

    keyboard.append(
        [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
    )

    return InlineKeyboardMarkup(keyboard)


def get_gully_context_keyboard(user_id: int, current_gully_id: Optional[int] = None):
    """Create a keyboard showing current gully context."""
    keyboard = [
        [
            InlineKeyboardButton("Switch Gully", callback_data=f"nav_switch_gully"),
            InlineKeyboardButton("Gully Info", callback_data=f"nav_gully_info"),
        ]
    ]

    if current_gully_id:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "« Back to Menu", callback_data=f"nav_back_main_{current_gully_id}"
                )
            ]
        )
    else:
        keyboard.append(
            [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
        )

    return InlineKeyboardMarkup(keyboard)


def get_match_list_keyboard(
    matches: List[Dict[str, Any]], current_page: int = 0, items_per_page: int = 5
) -> InlineKeyboardMarkup:
    """Create a keyboard for displaying a list of matches."""
    keyboard = []

    # Calculate pagination
    total_matches = len(matches)
    total_pages = (total_matches + items_per_page - 1) // items_per_page
    start_idx = current_page * items_per_page
    end_idx = min(start_idx + items_per_page, total_matches)

    # Get matches for current page
    current_matches = matches[start_idx:end_idx]

    # Add match buttons
    for match in current_matches:
        match_id = match.get("id")
        team1 = match.get("team1", "TBA")
        team2 = match.get("team2", "TBA")
        match_date = match.get("date", "TBA")

        # Add status indicator based on match status
        status = match.get("status", "scheduled")
        if status == "live":
            status_emoji = "🔴"  # Live
        elif status == "completed":
            status_emoji = "✅"  # Completed
        else:
            status_emoji = "⏳"  # Scheduled

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{status_emoji} {team1} vs {team2} ({match_date})",
                    callback_data=f"match_details_{match_id}",
                )
            ]
        )

    # Add navigation buttons
    nav_row = []

    if current_page > 0:
        nav_row.append(
            InlineKeyboardButton(
                "◀️ Previous", callback_data=f"match_page_{current_page-1}"
            )
        )

    # Create page indicator text
    page_text = f"Page {current_page+1}/{total_pages}"
    nav_row.append(InlineKeyboardButton(page_text, callback_data="match_noop"))

    if current_page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"match_page_{current_page+1}")
        )

    if nav_row:
        keyboard.append(nav_row)

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)


def get_match_details_keyboard(
    match_id: int, user_is_admin: bool = False
) -> InlineKeyboardMarkup:
    """Create a keyboard for match details."""
    keyboard = []

    # Add view teams button
    keyboard.append(
        [InlineKeyboardButton("View Teams", callback_data=f"match_teams_{match_id}")]
    )

    # Add view scorecard button
    keyboard.append(
        [
            InlineKeyboardButton(
                "View Scorecard", callback_data=f"match_scorecard_{match_id}"
            )
        ]
    )

    # Add admin-only buttons
    if user_is_admin:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Update Score", callback_data=f"match_update_{match_id}"
                )
            ]
        )

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_matches")])

    return InlineKeyboardMarkup(keyboard)
