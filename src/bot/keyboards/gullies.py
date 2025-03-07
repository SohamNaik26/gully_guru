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
    gullies: List[Dict[str, Any]], page: int = 1, items_per_page: int = 5
) -> InlineKeyboardMarkup:
    """Get keyboard for gully list with pagination."""
    # Calculate pagination
    total_gullies = len(gullies)
    total_pages = (total_gullies + items_per_page - 1) // items_per_page
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_gullies)

    # Get gullies for current page
    current_gullies = gullies[start_idx:end_idx]

    keyboard = []

    # Add gully buttons
    for gully in current_gullies:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{gully.get('name')} ({gully.get('member_count', 0)} members)",
                    callback_data=f"gully_select_{gully.get('id')}",
                )
            ]
        )

    # Add navigation buttons
    nav_buttons = []

    # Previous page button
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton("◀️ Previous", callback_data=f"gully_page_{page-1}")
        )

    # Page indicator
    nav_buttons.append(
        InlineKeyboardButton(f"{page}/{total_pages}", callback_data="nav_noop")
    )

    # Next page button
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"gully_page_{page+1}")
        )

    keyboard.append(nav_buttons)

    # Add create gully button
    keyboard.append(
        [InlineKeyboardButton("Create New Gully", callback_data="gully_create")]
    )

    # Add back button
    keyboard.append(
        [InlineKeyboardButton("Back to Menu", callback_data="nav_back_main")]
    )

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
