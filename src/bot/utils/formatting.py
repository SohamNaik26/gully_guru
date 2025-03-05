from typing import Dict, Any, Optional
from decimal import Decimal

def format_player_card(player: Dict[str, Any]) -> str:
    """Format a player card for display."""
    message = f"*{player['name']}*\n\n"
    
    # Basic info
    message += f"*Team:* {player['team']}\n"
    message += f"*Role:* {player['player_type']}\n"
    
    # Price info
    if player.get('sold_price'):
        message += f"*Price:* ₹{player['sold_price']} cr\n"
    elif player.get('base_price'):
        message += f"*Base Price:* ₹{player['base_price']} cr\n"
    
    # Stats if available
    if player.get('stats'):
        stats = player['stats']
        message += "\n*Stats:*\n"
        message += f"Matches: {stats.get('matches_played', 0)}\n"
        message += f"Runs: {stats.get('runs', 0)}\n"
        message += f"Wickets: {stats.get('wickets', 0)}\n"
        
        if stats.get('highest_score'):
            message += f"Highest Score: {stats['highest_score']}\n"
        
        if stats.get('best_bowling'):
            message += f"Best Bowling: {stats['best_bowling']}\n"
        
        if stats.get('fantasy_points'):
            message += f"Fantasy Points: {stats['fantasy_points']}\n"
    
    # Auction status if available
    if player.get('auction_status'):
        message += f"\n*Auction Status:* {player['auction_status'].capitalize()}\n"
        
        if player.get('current_bid'):
            message += f"Current Bid: ₹{player['current_bid']} cr\n"
            
        if player.get('highest_bidder'):
            message += f"Highest Bidder: {player['highest_bidder']}\n"
    
    # Team status
    if player.get('in_user_team', False):
        message += "\n*In Your Team:* Yes\n"
        if player.get('is_captain', False):
            message += "*Captain:* Yes\n"
    
    return message

def format_team_card(team: Dict[str, Any]) -> str:
    """Format a team card for display."""
    message = f"*Your Fantasy Team*\n\n"
    
    # Team value
    total_value = sum(Decimal(str(player.get('sold_price', 0))) for player in team.get('players', []))
    message += f"*Team Value:* ₹{total_value} cr\n"
    message += f"*Remaining Budget:* ₹{team.get('budget', 0)} cr\n"
    message += f"*Total Points:* {team.get('total_points', 0)}\n\n"
    
    # Players by category
    batsmen = [p for p in team.get('players', []) if p['player_type'] == 'BAT']
    bowlers = [p for p in team.get('players', []) if p['player_type'] == 'BOWL']
    all_rounders = [p for p in team.get('players', []) if p['player_type'] == 'ALL']
    wicket_keepers = [p for p in team.get('players', []) if p['player_type'] == 'WK']
    
    # Captain
    captain_id = team.get('captain_id')
    
    # Batsmen
    if batsmen:
        message += "*Batsmen:*\n"
        for player in batsmen:
            captain_mark = "👑 " if player['id'] == captain_id else ""
            message += f"• {captain_mark}{player['name']} ({player['team']})\n"
        message += "\n"
    
    # Bowlers
    if bowlers:
        message += "*Bowlers:*\n"
        for player in bowlers:
            captain_mark = "👑 " if player['id'] == captain_id else ""
            message += f"• {captain_mark}{player['name']} ({player['team']})\n"
        message += "\n"
    
    # All-rounders
    if all_rounders:
        message += "*All-rounders:*\n"
        for player in all_rounders:
            captain_mark = "👑 " if player['id'] == captain_id else ""
            message += f"• {captain_mark}{player['name']} ({player['team']})\n"
        message += "\n"
    
    # Wicket-keepers
    if wicket_keepers:
        message += "*Wicket-keepers:*\n"
        for player in wicket_keepers:
            captain_mark = "👑 " if player['id'] == captain_id else ""
            message += f"• {captain_mark}{player['name']} ({player['team']})\n"
        message += "\n"
    
    return message

def format_match_card(match: Dict[str, Any]) -> str:
    """Format a match card for display."""
    message = f"*{match['team1']} vs {match['team2']}*\n\n"
    
    # Match details
    message += f"*Date:* {match['date']}\n"
    message += f"*Venue:* {match['venue']}\n"
    
    # Match status
    if match.get('status') == 'completed':
        message += f"\n*Result:* {match.get('result', 'Unknown')}\n"
        
        if match.get('winner'):
            message += f"*Winner:* {match['winner']}\n"
        
        if match.get('player_of_match'):
            message += f"*Player of the Match:* {match['player_of_match']}\n"
    
    elif match.get('status') == 'live':
        message += f"\n*Live Score:*\n"
        
        if match.get('score_team1'):
            message += f"{match['team1']}: {match['score_team1']}\n"
        
        if match.get('score_team2'):
            message += f"{match['team2']}: {match['score_team2']}\n"
        
        if match.get('current_batsmen'):
            message += f"\n*Current Batsmen:* {match['current_batsmen']}\n"
        
        if match.get('current_bowler'):
            message += f"*Current Bowler:* {match['current_bowler']}\n"
    
    else:  # upcoming
        message += f"\n*Status:* Upcoming\n"
    
    # User prediction if available
    if match.get('user_prediction'):
        message += f"\n*Your Prediction:* {match['user_prediction']}\n"
    
    return message

def format_leaderboard(leaderboard: List[Dict[str, Any]]) -> str:
    """Format the leaderboard for display."""
    message = "*Fantasy Cricket Leaderboard*\n\n"
    
    for i, entry in enumerate(leaderboard):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
        message += f"{medal} *{entry['username']}* - {entry['total_points']} pts\n"
    
    return message

def format_transfer_listing(listing: Dict[str, Any]) -> str:
    """Format a transfer listing for display."""
    player = listing.get("player", {})
    seller = listing.get("seller", {})
    bids = listing.get("bids", [])
    
    # Format player details
    message = (
        f"*{player.get('name')}* ({player.get('team')})\n"
        f"Role: {player.get('player_type')}\n"
        f"Base Price: ₹{player.get('base_price')} cr\n\n"
        f"*Listing Details*\n"
        f"Seller: {seller.get('username') or 'Unknown'}\n"
        f"Minimum Price: ₹{listing.get('min_price')} cr\n"
    )
    
    # Add highest bid if any
    if bids:
        highest_bid = sorted(bids, key=lambda x: Decimal(str(x.get("bid_amount", 0))), reverse=True)[0]
        highest_bidder = highest_bid.get("bidder", {})
        
        message += (
            f"Highest Bid: ₹{highest_bid.get('bid_amount')} cr by "
            f"{highest_bidder.get('username') or 'Unknown'}\n"
            f"Total Bids: {len(bids)}\n"
        )
    else:
        message += "No bids yet\n"
    
    return message 