"""
Team management feature module for GullyGuru bot.
Handles team viewing and management.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Replace bot services with direct API client import
from src.api.api_client_instance import api_client

# Configure logging
logger = logging.getLogger(__name__)


async def my_team_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /my_team command.
    Shows the user's current team composition.
    """
    user = update.effective_user

    # Ensure user exists in database - using API client directly
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        # Create user if not exists
        db_user = await api_client.users.create_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

    if not db_user:
        await update.message.reply_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return

    # Get user's active gully - using API client directly
    active_gully = await api_client.users.get_active_gully(db_user["id"])
    if not active_gully:
        await update.message.reply_text(
            "You don't have an active gully. Please join a gully first using /join_gully in a group chat."
        )
        return

    # Get user's team in this gully - using API client directly
    team = await api_client.fantasy.get_user_team(db_user["id"], active_gully["id"])

    if not team or not team.get("players"):
        # User doesn't have a team yet
        await update.message.reply_text(
            f"You don't have a team in *{active_gully['name']}* yet.\n\n"
            f"Use /submit_squad to create your initial squad.",
            parse_mode="Markdown",
        )
        return

    # Format team information
    players = team.get("players", [])
    total_points = team.get("total_points", 0)

    message = (
        f"🏏 *Your Team in {active_gully['name']}* 🏏\n\n"
        f"*Total Points:* {total_points}\n\n"
        f"*Players:*\n"
    )

    for player in players:
        player_name = player.get("name", "Unknown")
        player_role = player.get("role", "Unknown")
        player_team = player.get("team", "Unknown")
        player_points = player.get("points", 0)

        message += (
            f"• {player_name} ({player_role}, {player_team}) - {player_points} pts\n"
        )

    # Add team management buttons
    keyboard = [
        [InlineKeyboardButton("Manage Team", callback_data="team_manage")],
        [InlineKeyboardButton("View Stats", callback_data="team_stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_team_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle callbacks for team management.
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    # Ensure user exists in database - using API client directly
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        # Create user if not exists
        db_user = await api_client.users.create_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

    if not db_user:
        await query.edit_message_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return

    # Get user's active gully - using API client directly
    active_gully = await api_client.users.get_active_gully(db_user["id"])
    if not active_gully:
        await query.edit_message_text(
            "You don't have an active gully. Please join a gully first using /join_gully in a group chat."
        )
        return

    if data == "team_manage":
        # Show team management options
        keyboard = [
            [InlineKeyboardButton("Transfer Players", callback_data="team_transfer")],
            [InlineKeyboardButton("Change Captain", callback_data="team_captain")],
            [InlineKeyboardButton("Back to Team", callback_data="team_view")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"*Team Management for {active_gully['name']}*\n\n"
            f"Select an option below:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif data == "team_stats":
        # Get team stats - using API client directly
        team_stats = await api_client.fantasy.get_team_stats(
            db_user["id"], active_gully["id"]
        )

        if not team_stats:
            await query.edit_message_text(
                "❌ Failed to retrieve team statistics. Please try again later."
            )
            return

        # Format stats message
        message = (
            f"📊 *Team Statistics for {active_gully['name']}* 📊\n\n"
            f"*Total Points:* {team_stats.get('total_points', 0)}\n"
            f"*Rank:* {team_stats.get('rank', 'N/A')}\n"
            f"*Matches Played:* {team_stats.get('matches_played', 0)}\n\n"
            f"*Best Performer:* {team_stats.get('best_performer', 'N/A')}\n"
            f"*Captain:* {team_stats.get('captain', 'N/A')}\n"
        )

        keyboard = [[InlineKeyboardButton("Back to Team", callback_data="team_view")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )

    elif data == "team_view":
        # Show team view again - using API client directly
        team = await api_client.fantasy.get_user_team(db_user["id"], active_gully["id"])

        if not team or not team.get("players"):
            await query.edit_message_text(
                f"You don't have a team in *{active_gully['name']}* yet.\n\n"
                f"Use /submit_squad to create your initial squad.",
                parse_mode="Markdown",
            )
            return

        # Format team information
        players = team.get("players", [])
        total_points = team.get("total_points", 0)

        message = (
            f"🏏 *Your Team in {active_gully['name']}* 🏏\n\n"
            f"*Total Points:* {total_points}\n\n"
            f"*Players:*\n"
        )

        for player in players:
            player_name = player.get("name", "Unknown")
            player_role = player.get("role", "Unknown")
            player_team = player.get("team", "Unknown")
            player_points = player.get("points", 0)

            message += f"• {player_name} ({player_role}, {player_team}) - {player_points} pts\n"

        # Add team management buttons
        keyboard = [
            [InlineKeyboardButton("Manage Team", callback_data="team_manage")],
            [InlineKeyboardButton("View Stats", callback_data="team_stats")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )
