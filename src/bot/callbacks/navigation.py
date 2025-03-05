from telegram import Update
from telegram.ext import ContextTypes

from src.bot.handlers import profile, players, team, auction, matches, leaderboard
from src.bot.keyboards.common import get_help_keyboard

async def handle_navigation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle navigation callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "nav_profile":
        await profile.profile_command(update, context)
    
    elif data == "nav_players":
        await players.list_players_command(update, context)
    
    elif data == "nav_team":
        await team.my_team_command(update, context)
    
    elif data == "nav_auction":
        await auction.auction_status_command(update, context)
    
    elif data == "nav_matches":
        await matches.list_matches_command(update, context)
    
    elif data == "nav_leaderboard":
        await leaderboard.leaderboard_command(update, context)
    
    elif data.startswith("nav_back_"):
        destination = data.split("_")[-1]
        
        if destination == "main":
            # Go back to main menu
            await query.edit_message_text(
                "What would you like to do?",
                reply_markup=get_help_keyboard()
            )
        
        elif destination == "players":
            # Go back to players list
            await players.list_players_command(update, context)
        
        elif destination == "team":
            # Go back to team view
            await team.my_team_command(update, context)
    
    elif data == "nav_noop":
        # No operation, just acknowledge the callback
        pass
    
    elif data.startswith("nav_page_"):
        # Handle pagination
        page = int(data.split("_")[-1])
        context.user_data["current_page"] = page
        
        # Determine which list to refresh based on context
        current_view = context.user_data.get("current_view", "players")
        
        if current_view == "players":
            await players.list_players_command(update, context)
        elif current_view == "matches":
            await matches.list_matches_command(update, context)
        elif current_view == "leaderboard":
            await leaderboard.leaderboard_command(update, context) 