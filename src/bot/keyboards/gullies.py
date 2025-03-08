from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any, Optional


def get_gully_management_keyboard(gully_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for gully management."""
    keyboard = [
        [
            InlineKeyboardButton(
                "View Members", callback_data=f"gully_members_{gully_id}"
            ),
            InlineKeyboardButton(
                "Settings", callback_data=f"gully_settings_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Start Auction", callback_data=f"gully_auction_{gully_id}"
            ),
            InlineKeyboardButton("View Teams", callback_data=f"gully_teams_{gully_id}"),
        ],
        [
            InlineKeyboardButton(
                "Schedule Match", callback_data=f"gully_schedule_{gully_id}"
            ),
            InlineKeyboardButton(
                "Leaderboard", callback_data=f"gully_leaderboard_{gully_id}"
            ),
        ],
        [InlineKeyboardButton("Back to Gullies", callback_data="nav_back_gullies")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_gully_list_keyboard(
    gullies: List[Dict[str, Any]],
    current_page: int = 0,
    items_per_page: int = 5,
    current_gully_id: Optional[int] = None,
) -> InlineKeyboardMarkup:
    """Create a keyboard for displaying a list of gullies."""
    keyboard = []

    # Calculate pagination
    total_gullies = len(gullies)
    total_pages = (total_gullies + items_per_page - 1) // items_per_page
    start_idx = current_page * items_per_page
    end_idx = min(start_idx + items_per_page, total_gullies)

    # Get gullies for current page
    current_gullies = gullies[start_idx:end_idx]

    # Add gully buttons
    for gully in current_gullies:
        gully_id = gully.get("id")
        gully_name = gully.get("name")
        gully_status = gully.get("status", "active")

        # Mark current gully
        prefix = "✓ " if gully_id == current_gully_id else ""

        # Add status indicator
        status_emoji = "🟢" if gully_status == "active" else "🔴"

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{prefix}{status_emoji} {gully_name}",
                    callback_data=f"select_gully_{gully_id}",
                )
            ]
        )

    # Add navigation buttons
    nav_row = []

    if current_page > 0:
        nav_row.append(
            InlineKeyboardButton(
                "◀️ Previous", callback_data=f"gully_page_{current_page-1}"
            )
        )

    nav_row.append(
        InlineKeyboardButton(
            f"Page {current_page+1}/{total_pages}", callback_data="gully_noop"
        )
    )

    if current_page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"gully_page_{current_page+1}")
        )

    if nav_row:
        keyboard.append(nav_row)

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)


def get_gully_settings_keyboard(gully_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for gully settings."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Edit Name", callback_data=f"gully_edit_name_{gully_id}"
            ),
            InlineKeyboardButton(
                "Edit Description", callback_data=f"gully_edit_desc_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Manage Admins", callback_data=f"gully_admins_{gully_id}"
            ),
            InlineKeyboardButton(
                "Privacy Settings", callback_data=f"gully_privacy_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Delete Gully", callback_data=f"gully_delete_{gully_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "Back to Gully", callback_data=f"gully_select_{gully_id}"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_gully_members_keyboard(
    gully_id: int, members: List[Dict[str, Any]], page: int = 1, items_per_page: int = 5
) -> InlineKeyboardMarkup:
    """Get keyboard for gully members with pagination."""
    # Calculate pagination
    total_members = len(members)
    total_pages = (total_members + items_per_page - 1) // items_per_page
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_members)

    # Get members for current page
    current_members = members[start_idx:end_idx]

    keyboard = []

    # Add member buttons
    for member in current_members:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{member.get('username')} ({member.get('role', 'member')})",
                    callback_data=f"member_view_{member.get('id')}",
                )
            ]
        )

    # Add navigation buttons
    nav_buttons = []

    # Previous page button
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton("◀️ Previous", callback_data=f"members_page_{page-1}")
        )

    # Page indicator
    nav_buttons.append(
        InlineKeyboardButton(f"{page}/{total_pages}", callback_data="nav_noop")
    )

    # Next page button
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"members_page_{page+1}")
        )

    keyboard.append(nav_buttons)

    # Add back button
    keyboard.append(
        [
            InlineKeyboardButton(
                "Back to Gully", callback_data=f"gully_select_{gully_id}"
            )
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def get_gully_context_keyboard(
    current_gully_id: Optional[int] = None,
    show_back: bool = True,
) -> InlineKeyboardMarkup:
    """Create a keyboard showing the current gully context."""
    keyboard = []

    # Add switch gully button
    keyboard.append(
        [InlineKeyboardButton("Switch Gully", callback_data="switch_gully")]
    )

    # Add gully info button if a gully is selected
    if current_gully_id:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Gully Info", callback_data=f"gully_info_{current_gully_id}"
                )
            ]
        )

    # Add back button if requested
    if show_back:
        keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)
