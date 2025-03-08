from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List, Optional


def get_player_filters_keyboard(
    teams: List[str] = None, player_types: List[str] = None
) -> InlineKeyboardMarkup:
    """Create a keyboard for filtering players by team and type."""
    keyboard = []

    # Add team filter buttons (2 per row)
    if teams:
        team_rows = []
        current_row = []

        for team in teams:
            current_row.append(
                InlineKeyboardButton(team, callback_data=f"filter_team_{team}")
            )

            if len(current_row) == 2:
                team_rows.append(current_row)
                current_row = []

        if current_row:
            team_rows.append(current_row)

        keyboard.extend(team_rows)

    # Add player type filter buttons (all in one row)
    if player_types:
        type_row = []

        for player_type in player_types:
            type_row.append(
                InlineKeyboardButton(
                    player_type, callback_data=f"filter_type_{player_type}"
                )
            )

        keyboard.append(type_row)

    # Add clear filters and back buttons
    keyboard.append(
        [
            InlineKeyboardButton("Clear Filters", callback_data="clear_filters"),
            InlineKeyboardButton("« Back", callback_data="back_to_players"),
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def get_player_details_keyboard(
    player_id: int,
    in_user_team: bool = False,
    auction_active: bool = False,
    is_captain: bool = False,
) -> InlineKeyboardMarkup:
    """Create a keyboard for player details."""
    keyboard = []

    # Add auction-related buttons if auction is active
    if auction_active:
        keyboard.append(
            [InlineKeyboardButton("Place Bid", callback_data=f"bid_{player_id}")]
        )

    # Add team management buttons if player is in user's team
    if in_user_team:
        if is_captain:
            keyboard.append(
                [InlineKeyboardButton("Captain ✓", callback_data=f"captain_info")]
            )
        else:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "Set as Captain", callback_data=f"set_captain_{player_id}"
                    )
                ]
            )

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_players")])

    return InlineKeyboardMarkup(keyboard)


def get_my_team_keyboard(
    players: List[Dict[str, Any]], captain_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    """Create a keyboard for viewing and managing user's team."""
    keyboard = []

    # Group players by type
    player_types = {"BAT": [], "BOWL": [], "ALL": [], "WK": []}

    for player in players:
        player_type = player.get("type", "BAT")
        if player_type in player_types:
            player_types[player_type].append(player)

    # Add buttons for each player type
    for player_type, type_players in player_types.items():
        if type_players:
            # Add header for player type
            header_text = "--- " + player_type + " ---"
            keyboard.append([InlineKeyboardButton(header_text, callback_data="noop")])

            # Add player buttons
            for player in type_players:
                player_id = player.get("id")
                player_name = player.get("name")
                is_captain = player_id == captain_id
                captain_mark = " (C)" if is_captain else ""

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{player_name}{captain_mark}",
                            callback_data=f"view_player_{player_id}",
                        )
                    ]
                )

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)
