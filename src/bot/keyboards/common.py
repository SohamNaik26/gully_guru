from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_help_keyboard():
    """Create a keyboard with common commands."""
    keyboard = [
        [
            InlineKeyboardButton("👤 Profile", callback_data="nav_profile"),
            InlineKeyboardButton("🏏 Players", callback_data="nav_players"),
        ],
        [
            InlineKeyboardButton("👥 My Team", callback_data="nav_team"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="nav_leaderboard"),
        ],
        [
            InlineKeyboardButton("🔄 Auction", callback_data="nav_auction"),
            InlineKeyboardButton("🗓️ Matches", callback_data="nav_matches"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button(destination="main"):
    """Create a back button."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("« Back", callback_data=f"nav_back_{destination}")]]
    )


def get_pagination_keyboard(current_page, total_pages, base_callback="nav_page"):
    """Create pagination buttons."""
    keyboard = []

    # Add page navigation
    navigation = []
    if current_page > 0:
        navigation.append(
            InlineKeyboardButton(
                "« Prev", callback_data=f"{base_callback}_{current_page-1}"
            )
        )

    navigation.append(
        InlineKeyboardButton(
            f"{current_page+1}/{total_pages}", callback_data="nav_noop"
        )
    )

    if current_page < total_pages - 1:
        navigation.append(
            InlineKeyboardButton(
                "Next »", callback_data=f"{base_callback}_{current_page+1}"
            )
        )

    keyboard.append(navigation)

    # Add back button
    keyboard.append(
        [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
    )

    return InlineKeyboardMarkup(keyboard)
