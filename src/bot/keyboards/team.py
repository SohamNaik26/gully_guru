from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List

def get_team_management_keyboard():
    """Create a keyboard for team management."""
    keyboard = [
        [
            InlineKeyboardButton("Set Captain", callback_data="team_captain"),
            InlineKeyboardButton("Transfer Players", callback_data="team_transfer")
        ],
        [
            InlineKeyboardButton("View Players", callback_data="nav_players"),
            InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_captain_selection_keyboard(team: Dict[str, Any]):
    """Create a keyboard for captain selection."""
    keyboard = []
    
    # Group players by type for better organization
    players_by_type = {
        "BAT": [],
        "BOWL": [],
        "ALL": [],
        "WK": []
    }
    
    for player in team.get('players', []):
        player_type = player.get('player_type', 'BAT')
        players_by_type[player_type].append(player)
    
    # Add buttons for each player
    for player_type, players in players_by_type.items():
        if players:
            for player in players:
                captain_mark = "👑 " if player['id'] == team.get('captain_id') else ""
                keyboard.append([
                    InlineKeyboardButton(
                        f"{captain_mark}{player['name']} ({player_type})",
                        callback_data=f"team_set_captain_{player['id']}"
                    )
                ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("« Back to Team", callback_data="nav_back_team")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_player_removal_keyboard(team: Dict[str, Any]):
    """Create a keyboard for removing players."""
    keyboard = []
    
    # Group players by type for better organization
    players_by_type = {
        "BAT": [],
        "BOWL": [],
        "ALL": [],
        "WK": []
    }
    
    for player in team.get('players', []):
        player_type = player.get('player_type', 'BAT')
        players_by_type[player_type].append(player)
    
    # Add buttons for each player
    for player_type, players in players_by_type.items():
        if players:
            for player in players:
                keyboard.append([
                    InlineKeyboardButton(
                        f"Remove: {player['name']} ({player_type})",
                        callback_data=f"team_remove_{player['id']}"
                    )
                ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("« Back to Team", callback_data="nav_back_team")
    ])
    
    return InlineKeyboardMarkup(keyboard) 