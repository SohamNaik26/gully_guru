from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List
from decimal import Decimal
from src.bot.utils.auction import calculate_min_bid_increment, calculate_max_bid


def get_auction_keyboard(player_id: int) -> InlineKeyboardMarkup:
    """Create a keyboard for auction actions."""
    keyboard = [
        [InlineKeyboardButton("Place Bid", callback_data=f"auction_bid_{player_id}")],
        [
            InlineKeyboardButton(
                "View Player Details", callback_data=f"view_player_{player_id}"
            )
        ],
        [InlineKeyboardButton("« Back", callback_data="auction_status")],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_auction_history_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Create a keyboard for auction history navigation."""
    keyboard = []

    # Add navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                "« Previous", callback_data=f"auction_history_page_{page-1}"
            )
        )

    nav_buttons.append(
        InlineKeyboardButton("Next »", callback_data=f"auction_history_page_{page+1}")
    )

    if nav_buttons:
        keyboard.append(nav_buttons)

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="auction_status")])

    return InlineKeyboardMarkup(keyboard)


def get_bid_keyboard(
    current_bid: Decimal,
    base_price: Decimal,
    user_budget: Decimal,
    remaining_slots: int = 1,
) -> InlineKeyboardMarkup:
    """Create a keyboard with bid options."""
    # Calculate minimum bid
    min_increment = calculate_min_bid_increment(current_bid)
    min_bid = max(current_bid + min_increment, base_price)

    # Calculate maximum bid
    max_bid = calculate_max_bid(user_budget, remaining_slots)

    # Generate bid options
    bid_options = []
    current_bid_value = min_bid

    # Add up to 5 bid options
    for _ in range(5):
        if current_bid_value <= max_bid:
            bid_options.append(current_bid_value)
            current_bid_value += min_increment
        else:
            break

    # Create keyboard rows with 2 buttons per row
    keyboard = []
    row = []

    for bid in bid_options:
        row.append(InlineKeyboardButton(f"₹{bid} cr", callback_data=f"place_bid_{bid}"))

        if len(row) == 2:
            keyboard.append(row)
            row = []

    # Add any remaining buttons
    if row:
        keyboard.append(row)

    # Add custom bid option
    keyboard.append([InlineKeyboardButton("Custom Bid", callback_data="custom_bid")])

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="auction_status")])

    return InlineKeyboardMarkup(keyboard)


def get_squad_selection_keyboard(
    available_players: List[Dict[str, Any]],
    selected_players: List[int],
    page: int = 0,
    items_per_page: int = 10,
) -> InlineKeyboardMarkup:
    """Create a keyboard for squad selection during Round 0."""
    # Calculate pagination
    total_players = len(available_players)
    total_pages = (total_players + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, total_players)

    # Get players for current page
    current_players = available_players[start_idx:end_idx]

    keyboard = []

    # Add player buttons
    for player in current_players:
        player_id = player.get("id")
        is_selected = player_id in selected_players
        prefix = "✅ " if is_selected else ""
        action = "remove" if is_selected else "add"

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{prefix}{player.get('name')} ({player.get('team')}) - ₹{player.get('base_price')} cr",
                    callback_data=f"squad_{action}_{player_id}",
                )
            ]
        )

    # Add navigation buttons
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton("◀️ Previous", callback_data=f"squad_page_{page-1}")
        )

    nav_row.append(
        InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="squad_noop")
    )

    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"squad_page_{page+1}")
        )

    keyboard.append(nav_row)

    # Add filter buttons
    filter_row = [
        InlineKeyboardButton("Filter by Team", callback_data="squad_filter_team"),
        InlineKeyboardButton("Filter by Type", callback_data="squad_filter_type"),
    ]
    keyboard.append(filter_row)

    # Add submit button
    if len(selected_players) == 18:
        keyboard.append(
            [InlineKeyboardButton("Submit Squad ✅", callback_data="squad_submit")]
        )
    else:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Selected: {len(selected_players)}/18",
                    callback_data="squad_view_selected",
                )
            ]
        )

    # Add cancel button
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="squad_cancel")])

    return InlineKeyboardMarkup(keyboard)
