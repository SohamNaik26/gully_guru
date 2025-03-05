from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List
from decimal import Decimal
from src.bot.utils.auction import calculate_min_bid_increment, calculate_max_bid

def get_auction_keyboard(player_id: int) -> InlineKeyboardMarkup:
    """Create a keyboard for auction actions."""
    keyboard = [
        [InlineKeyboardButton("Place Bid", callback_data=f"auction_bid_{player_id}")],
        [InlineKeyboardButton("View Player Details", callback_data=f"view_player_{player_id}")],
        [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_bid_keyboard(current_bid: Decimal, base_price: Decimal, user_budget: Decimal, remaining_slots: int = 1) -> InlineKeyboardMarkup:
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
    keyboard.append([InlineKeyboardButton("« Back", callback_data=f"auction_status")])
    
    return InlineKeyboardMarkup(keyboard)

def get_auction_history_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboard for auction history."""
    keyboard = [
        [InlineKeyboardButton("Current Auction", callback_data="nav_auction")],
        [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
    ]
    
    return InlineKeyboardMarkup(keyboard) 