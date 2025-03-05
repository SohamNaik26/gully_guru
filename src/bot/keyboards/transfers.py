from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List
from decimal import Decimal

def get_transfer_menu_keyboard(window_status: str) -> InlineKeyboardMarkup:
    """Create a keyboard for transfer menu based on window status."""
    keyboard = []
    
    if window_status == "active":
        keyboard = [
            [InlineKeyboardButton("View Available Players", callback_data="view_available_players")],
            [InlineKeyboardButton("List Player for Sale", callback_data="list_player_for_sale")],
            [InlineKeyboardButton("My Listings", callback_data="view_my_listings")],
            [InlineKeyboardButton("My Bids", callback_data="view_my_bids")],
            [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
        ]
    elif window_status == "pending":
        keyboard = [
            [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
        ]
    else:  # closed
        keyboard = [
            [InlineKeyboardButton("View Last Window Results", callback_data="view_transfer_results")],
            [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def get_player_listing_keyboard(listing: Dict[str, Any], user: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Create a keyboard for viewing a player listing."""
    keyboard = []
    
    # Check if this is user's own listing
    if listing.get("seller_id") == user.get("id"):
        # User is the seller
        bids = listing.get("bids", [])
        
        if bids:
            # Show accept highest bid option
            highest_bid = sorted(bids, key=lambda x: Decimal(str(x.get("bid_amount", 0))), reverse=True)[0]
            
            keyboard = [
                [InlineKeyboardButton(
                    f"Accept Bid: ₹{highest_bid.get('bid_amount')} cr", 
                    callback_data=f"accept_bid_{highest_bid.get('id')}"
                )],
                [InlineKeyboardButton(
                    "Cancel Listing", 
                    callback_data=f"cancel_listing_{listing.get('id')}"
                )]
            ]
        else:
            # No bids yet
            keyboard = [
                [InlineKeyboardButton(
                    "Cancel Listing", 
                    callback_data=f"cancel_listing_{listing.get('id')}"
                )]
            ]
    else:
        # User is a potential buyer
        # Check if user already has a bid on this listing
        user_has_bid = False
        for bid in listing.get("bids", []):
            if bid.get("bidder_id") == user.get("id"):
                user_has_bid = True
                break
        
        if user_has_bid:
            keyboard = [
                [InlineKeyboardButton(
                    "Update Bid", 
                    callback_data=f"bid_on_listing_{listing.get('id')}"
                )]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton(
                    "Place Bid", 
                    callback_data=f"bid_on_listing_{listing.get('id')}"
                )]
            ]
    
    # Add back button
    keyboard.append([InlineKeyboardButton("« Back to Available Players", callback_data="view_available_players")])
    
    return InlineKeyboardMarkup(keyboard)

def get_bid_confirmation_keyboard(listing_id: int, bid_amount: Decimal, is_free_bid: bool) -> InlineKeyboardMarkup:
    """Create a keyboard for confirming a bid."""
    keyboard = [
        [InlineKeyboardButton(
            "Confirm Bid", 
            callback_data=f"confirm_bid_{listing_id}_{bid_amount}_{is_free_bid}"
        )],
        [InlineKeyboardButton(
            "Cancel", 
            callback_data=f"view_player_listing_{listing_id}"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_player_listing_keyboard_for_list(listings: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Create a keyboard with buttons for each listing."""
    keyboard = []
    
    # Add buttons for each listing (up to 10)
    for i, listing in enumerate(listings[:10], 1):
        player = listing.get("player", {})
        keyboard.append([
            InlineKeyboardButton(
                f"{i}. {player.get('name')} - ₹{listing.get('min_price')} cr",
                callback_data=f"view_player_listing_{listing.get('id')}"
            )
        ])
    
    # Add navigation buttons
    keyboard.append([InlineKeyboardButton("« Back to Transfers", callback_data="nav_transfers")])
    
    return InlineKeyboardMarkup(keyboard) 