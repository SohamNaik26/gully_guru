from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, List, Optional

from src.bot.bot import api_client
from src.bot.utils.formatting import format_team_card
from src.bot.keyboards.team import get_team_management_keyboard, get_captain_selection_keyboard

async def my_team_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /myteam command."""
    user = update.effective_user
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    
    if not db_user:
        await update.effective_message.reply_text(
            "You need to register first. Use /start to register."
        )
        return
    
    # Get user's team
    team = await api_client.get_user_team(db_user['id'])
    
    if not team or not team.get('players'):
        await update.effective_message.reply_text(
            "You don't have any players in your team yet.\n\n"
            "Use /players to browse available players and add them to your team."
        )
        return
    
    # Format team card
    message = format_team_card(team)
    
    # Create keyboard
    keyboard = get_team_management_keyboard()
    
    # Send or edit message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await update.effective_message.reply_text(
            message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

async def set_captain_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /captain command."""
    user = update.effective_user
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return
    
    # Get user's team
    team = await api_client.get_user_team(db_user['id'])
    
    if not team or not team.get('players'):
        await update.message.reply_text(
            "You don't have any players in your team yet.\n\n"
            "Use /players to browse available players and add them to your team."
        )
        return
    
    # Show captain selection keyboard
    message = "Select a player to be your team captain:"
    keyboard = get_captain_selection_keyboard(team)
    
    await update.message.reply_text(
        message,
        reply_markup=keyboard
    )

async def transfer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /transfer command."""
    user = update.effective_user
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return
    
    # Show transfer options
    message = (
        "*Transfer Players*\n\n"
        "You can transfer players in and out of your team.\n\n"
        "• To add players: Use /players to browse and add players\n"
        "• To remove players: View your team with /myteam and select players to remove\n\n"
        "Your remaining budget: ₹{} cr".format(db_user['budget'])
    )
    
    # Create keyboard
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Browse Players", callback_data="nav_players")],
        [InlineKeyboardButton("View My Team", callback_data="nav_team")]
    ])
    
    await update.message.reply_text(
        message,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def check_team_composition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /check_team command to validate team composition."""
    user = update.effective_user
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return
    
    # Validate team composition
    validation = await api_client.validate_user_team(db_user.get("id"))
    
    # Format message
    if validation.get("valid"):
        message = "✅ *Team Composition Valid*\n\n"
    else:
        message = "❌ *Team Composition Invalid*\n\n"
        message += f"{validation.get('message')}\n\n"
    
    # Add role counts
    role_counts = validation.get("role_counts", {})
    message += "*Current Squad:*\n"
    message += f"Total Players: {validation.get('total_players', 0)}/18\n"
    message += f"Batsmen: {role_counts.get('BAT', 0)}\n"
    message += f"Bowlers: {role_counts.get('BOWL', 0)}\n"
    message += f"All-Rounders: {role_counts.get('ALL', 0)}\n"
    message += f"Wicket-Keepers: {role_counts.get('WK', 0)}\n\n"
    
    # Add requirements
    message += "*Requirements:*\n"
    message += "- Maximum 18 players total\n"
    message += "- At least 1 batsman\n"
    message += "- At least 1 bowler\n"
    message += "- At least 1 all-rounder\n"
    message += "- At least 1 wicket-keeper\n"
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown"
    ) 