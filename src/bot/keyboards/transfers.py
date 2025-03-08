from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List
from decimal import Decimal


def get_transfer_menu_keyboard(window_status: str = "closed") -> InlineKeyboardMarkup:
    """Create a keyboard for the transfer menu based on window status."""
    keyboard = []

    # Add buttons based on window status
    if window_status == "active":
        # Active transfer window
        keyboard.append(
            [
                InlineKeyboardButton(
                    "View Available Players", callback_data="transfer_view_players"
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    "List Player for Sale", callback_data="transfer_list_player"
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    "View My Listings", callback_data="transfer_my_listings"
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    "View All Listings", callback_data="transfer_all_listings"
                )
            ]
        )
    elif window_status == "pending":
        # Pending transfer window
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Transfer Window Opening Soon", callback_data="transfer_info"
                )
            ]
        )
        keyboard.append([InlineKeyboardButton("View My Team", callback_data="my_team")])
    else:
        # Closed transfer window
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Transfer Window Closed", callback_data="transfer_info"
                )
            ]
        )
        keyboard.append([InlineKeyboardButton("View My Team", callback_data="my_team")])

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)


def get_player_listing_keyboard(
    listing: Dict[str, Any], is_seller: bool = False
) -> InlineKeyboardMarkup:
    """Create a keyboard for viewing a specific player listing."""
    keyboard = []

    listing_id = listing.get("id")
    player_id = listing.get("player_id")

    # Add seller-specific buttons
    if is_seller:
        # Seller can accept bids or cancel listing
        if listing.get("has_bids", False):
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "Accept Highest Bid",
                        callback_data=f"transfer_accept_{listing_id}",
                    )
                ]
            )

        keyboard.append(
            [
                InlineKeyboardButton(
                    "Cancel Listing", callback_data=f"transfer_cancel_{listing_id}"
                )
            ]
        )
    else:
        # Buyer can place a bid
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Place Bid", callback_data=f"transfer_bid_{listing_id}"
                )
            ]
        )

    # Add view player details button
    keyboard.append(
        [
            InlineKeyboardButton(
                "View Player Details", callback_data=f"view_player_{player_id}"
            )
        ]
    )

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_transfers")])

    return InlineKeyboardMarkup(keyboard)


def get_bid_confirmation_keyboard(
    listing_id: int, bid_amount: Decimal
) -> InlineKeyboardMarkup:
    """Create a keyboard for confirming a bid."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"Confirm Bid: ₹{bid_amount} cr",
                callback_data=f"transfer_confirm_bid_{listing_id}_{bid_amount}",
            )
        ],
        [InlineKeyboardButton("Cancel", callback_data=f"transfer_view_{listing_id}")],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_player_listing_keyboard_for_list(
    listings: List[Dict[str, Any]], current_page: int = 0, items_per_page: int = 5
) -> InlineKeyboardMarkup:
    """Create a keyboard with buttons for each player listing."""
    keyboard = []

    # Calculate pagination
    total_listings = len(listings)
    total_pages = (total_listings + items_per_page - 1) // items_per_page
    start_idx = current_page * items_per_page
    end_idx = min(start_idx + items_per_page, total_listings)

    # Get listings for current page
    current_listings = listings[start_idx:end_idx]

    # Add listing buttons
    for listing in current_listings:
        listing_id = listing.get("id")
        player_name = listing.get("player_name", "Unknown")
        player_team = listing.get("player_team", "")
        player_type = listing.get("player_type", "")
        base_price = listing.get("base_price", 0)
        highest_bid = listing.get("highest_bid", 0)

        # Format button text
        if highest_bid > 0:
            price_text = f"₹{highest_bid} cr (Current Bid)"
        else:
            price_text = f"₹{base_price} cr (Base)"

        button_text = f"{player_name} ({player_team}) - {player_type} - {price_text}"

        keyboard.append(
            [
                InlineKeyboardButton(
                    button_text, callback_data=f"transfer_view_{listing_id}"
                )
            ]
        )

    # Add navigation buttons
    nav_row = []

    if current_page > 0:
        nav_row.append(
            InlineKeyboardButton(
                "◀️ Previous", callback_data=f"transfer_page_{current_page-1}"
            )
        )

    # Create page indicator text
    page_text = f"Page {current_page+1}/{total_pages}"
    nav_row.append(InlineKeyboardButton(page_text, callback_data="transfer_noop"))

    if current_page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                "Next ▶️", callback_data=f"transfer_page_{current_page+1}"
            )
        )

    if nav_row:
        keyboard.append(nav_row)

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_transfers")])

    return InlineKeyboardMarkup(keyboard)
