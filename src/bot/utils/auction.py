from decimal import Decimal
from typing import Dict, Any, List, Optional

def calculate_min_bid_increment(current_bid: Decimal) -> Decimal:
    """
    Calculate the minimum bid increment based on the current bid amount.
    
    Rules:
    - For bids < 1 Cr: +0.10 Cr
    - For bids < 2 Cr: +0.20 Cr
    - For bids < 5 Cr: +0.50 Cr
    - For bids >= 5 Cr: +1.00 Cr
    """
    if current_bid < Decimal("1.0"):
        return Decimal("0.10")
    elif current_bid < Decimal("2.0"):
        return Decimal("0.20")
    elif current_bid < Decimal("5.0"):
        return Decimal("0.50")
    else:
        return Decimal("1.00")

def calculate_max_bid(user_budget: Decimal, remaining_slots: int) -> Decimal:
    """
    Calculate the maximum bid a user can place while ensuring they can complete their squad.
    
    Args:
        user_budget: User's current budget in Cr
        remaining_slots: Number of players still needed to complete the 18-player squad
    
    Returns:
        Maximum bid amount in Cr
    """
    if remaining_slots <= 0:
        return user_budget
    
    # Reserve budget for remaining players (0.20 Cr per player)
    reserve_budget = Decimal("0.20") * Decimal(str(remaining_slots - 1))
    
    # Maximum bid is current budget minus reserve budget
    max_bid = user_budget - reserve_budget
    
    # Ensure max bid is not negative
    return max(max_bid, Decimal("0"))

def validate_team_composition(players: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate team composition based on role requirements.
    
    Requirements:
    - At least 1 batsman
    - At least 1 bowler
    - At least 1 all-rounder
    - At least 1 wicket-keeper
    - Maximum 18 players total
    
    Args:
        players: List of player objects with 'player_type' field
    
    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    if len(players) > 18:
        return {
            "valid": False,
            "message": "Squad exceeds maximum of 18 players"
        }
    
    # Count players by role
    role_counts = {
        "BAT": 0,
        "BOWL": 0,
        "ALL": 0,
        "WK": 0
    }
    
    for player in players:
        player_type = player.get("player_type", "")
        if player_type in role_counts:
            role_counts[player_type] += 1
    
    # Check minimum requirements
    missing_roles = []
    
    if role_counts["BAT"] < 1:
        missing_roles.append("batsman")
    
    if role_counts["BOWL"] < 1:
        missing_roles.append("bowler")
    
    if role_counts["ALL"] < 1:
        missing_roles.append("all-rounder")
    
    if role_counts["WK"] < 1:
        missing_roles.append("wicket-keeper")
    
    if missing_roles:
        return {
            "valid": False,
            "message": f"Squad must include at least 1 {', 1 '.join(missing_roles)}"
        }
    
    return {
        "valid": True,
        "message": "Team composition is valid"
    } 