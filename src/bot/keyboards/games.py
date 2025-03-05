from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List, Optional

def get_gully_management_keyboard(gully_id: int):
    """Create a keyboard for gully management."""
    keyboard = [
        [
            InlineKeyboardButton("Join Gully", callback_data=f"gully_join_{gully_id}"),
            InlineKeyboardButton("View Leaderboard", callback_data=f"gully_leaderboard_{gully_id}")
        ],
        [
            InlineKeyboardButton("Start Auction", callback_data=f"gully_start_auction_{gully_id}"),
            InlineKeyboardButton("Open Transfers", callback_data=f"gully_open_transfers_{gully_id}")
        ],
        [
            InlineKeyboardButton("« Back to Gullies", callback_data="nav_my_gullies")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_gully_list_keyboard(gullies: List[Dict[str, Any]], action: str = "switch"):
    """Create a keyboard for gully list."""
    keyboard = []
    
    for gully in gullies:
        keyboard.append([
            InlineKeyboardButton(
                f"{gully.get('name')} ({gully.get('status')})",
                callback_data=f"{action}_gully_{gully.get('id')}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_gully_context_keyboard(user_id: int, current_gully_id: Optional[int] = None):
    """Create a keyboard showing current gully context."""
    keyboard = [
        [
            InlineKeyboardButton("Switch Gully", callback_data=f"nav_switch_gully"),
            InlineKeyboardButton("Gully Info", callback_data=f"nav_gully_info")
        ]
    ]
    
    if current_gully_id:
        keyboard.append([
            InlineKeyboardButton("« Back to Menu", callback_data=f"nav_back_main_{current_gully_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")
        ])
    
    return InlineKeyboardMarkup(keyboard) 