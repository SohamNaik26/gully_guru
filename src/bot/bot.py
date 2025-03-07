#!/usr/bin/env python
"""
Main bot module for GullyGuru.
"""

import logging
import os
from dotenv import load_dotenv
from telegram import BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from decimal import Decimal
from sqlmodel import select

from src.db.session import get_session
from src.db.models import User, Player, PlayerStats, UserPlayer
from src.config import settings
from src.bot.api_client_instance import api_client
from src.bot.handlers import start, players, team, auction
from src.bot.handlers.game_guide import game_guide_command, handle_term_callback
from src.bot.callbacks import (
    navigation,
    players as player_callbacks,
    auction as auction_callbacks,
)
from src.bot.handlers.games import register_handlers as register_game_handlers
from src.bot.handlers.start import start_command, register_command
from src.bot.handlers.help import help_command
from src.bot.handlers.game_guide import game_guide_command
from src.bot.handlers.profile import profile_command, budget_command
from src.bot.handlers import players, team, auction, navigation, player_callbacks
from src.bot.handlers.admin import (
    admin_panel_command,
    add_admin_command,
    remove_admin_command,
    nominate_admin_command,
    gully_settings_command,
    invite_link_command,
    setup_wizard_command,
    admin_roles_command,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create global API client
# api_client = APIClient()


# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user

    # Check if user exists in our database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        # Create new user
        new_user = {
            "telegram_id": user.id,
            "username": user.username or f"user_{user.id}",
            "full_name": user.full_name,
            "budget": 120.0,
            "total_points": 0.0,
        }
        db_user = await api_client.create_user(new_user)

        if not db_user:
            await update.message.reply_text(
                "Sorry, there was an error creating your account. Please try again later."
            )
            return

        welcome_message = (
            f"Welcome to GullyGuru, {user.full_name}! 🏏\n\n"
            f"Your account has been created with a budget of ₹{db_user['budget']} crores.\n"
            f"Use /help to see available commands."
        )
    else:
        welcome_message = (
            f"Welcome back to GullyGuru, {user.full_name}! 🏏\n\n"
            f"Your current budget is ₹{db_user['budget']} crores.\n"
            f"Your total points: {db_user['total_points']}\n"
            f"Use /help to see available commands."
        )

    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        "🏏 *GullyGuru Fantasy Cricket* 🏏\n\n"
        "Available commands:\n\n"
        "/start - Start or restart the bot\n"
        "/help - Show this help message\n"
        "/profile - View your profile\n"
        "/players - Browse available players\n"
        "/myteam - View your team\n"
        "/budget - Check your remaining budget\n"
        "/leaderboard - View the points leaderboard\n"
        "/matches - View upcoming matches\n"
        "/stats - View player statistics\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /profile command."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You don't have an account yet. Use /start to create one."
        )
        return

    # Get user's team
    async with get_session() as session:
        # Use direct database access for complex queries
        user_id = db_user["id"]

        # Get user's players
        stmt = (
            "SELECT p.name, p.team, p.player_type, upl.price "
            "FROM user_player_links upl "
            "JOIN players p ON upl.player_id = p.id "
            "WHERE upl.user_id = :user_id"
        )
        result = await session.execute(stmt, {"user_id": user_id})
        players = result.fetchall()

        # Format profile message
        profile_text = (
            f"📊 *Your Profile* 📊\n\n"
            f"Name: {db_user['full_name']}\n"
            f"Username: @{db_user['username']}\n"
            f"Budget: ₹{db_user['budget']} crores\n"
            f"Total Points: {db_user['total_points']}\n\n"
            f"Team Size: {len(players)} players\n"
        )

        if players:
            profile_text += "\n*Your Team:*\n"
            for player in players:
                profile_text += f"• {player.name} ({player.team}) - {player.player_type} - ₹{player.price} cr\n"
        else:
            profile_text += "\nYou haven't selected any players yet. Use /players to browse available players."

    await update.message.reply_text(profile_text, parse_mode="Markdown")


async def list_players_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /players command."""
    # Parse arguments for filtering
    args = context.args

    team = None
    player_type = None
    page = 0

    for arg in args:
        if arg.startswith("team="):
            team = arg.split("=")[1]
        elif arg.startswith("type="):
            player_type = arg.split("=")[1]
        elif arg.startswith("page="):
            try:
                page = max(0, int(arg.split("=")[1]) - 1)
            except ValueError:
                pass

    # Get players from API
    limit = 5
    skip = page * limit
    players = await api_client.get_players(
        skip=skip, limit=limit, team=team, player_type=player_type
    )

    if not players:
        await update.message.reply_text("No players found with the specified filters.")
        return

    # Create message with player list
    message = "🏏 *Available Players* 🏏\n\n"

    for player in players:
        message += (
            f"*{player['name']}* ({player['team']})\n"
            f"Type: {player['player_type']}\n"
            f"Price: ₹{player['sold_price'] or player['base_price'] or 'TBD'} cr\n\n"
        )

    # Add pagination buttons
    keyboard = [
        [
            InlineKeyboardButton(
                "Previous", callback_data=f"players_page_{max(0, page-1)}"
            ),
            InlineKeyboardButton("Next", callback_data=f"players_page_{page+1}"),
        ],
        [
            InlineKeyboardButton(
                "View Details", callback_data=f"player_details_{players[0]['id']}"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def my_team_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /myteam command."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You don't have an account yet. Use /start to create one."
        )
        return

    # Get user's team
    async with get_session() as session:
        user_id = db_user["id"]

        # Get user's players with stats
        stmt = (
            "SELECT p.id, p.name, p.team, p.player_type, upl.price, "
            "ps.runs, ps.wickets, ps.matches_played "
            "FROM user_player_links upl "
            "JOIN players p ON upl.player_id = p.id "
            "LEFT JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE upl.user_id = :user_id"
        )
        result = await session.execute(stmt, {"user_id": user_id})
        players = result.fetchall()

    if not players:
        await update.message.reply_text(
            "You haven't selected any players yet. Use /players to browse available players."
        )
        return

    # Format team message
    team_text = f"🏏 *Your Fantasy Team* 🏏\n\nBudget: ₹{db_user['budget']} crores\n\n"

    # Group players by type
    batsmen = [p for p in players if p.player_type == "BAT"]
    bowlers = [p for p in players if p.player_type == "BOWL"]
    all_rounders = [p for p in players if p.player_type == "ALL"]
    wicket_keepers = [p for p in players if p.player_type == "WK"]

    # Add batsmen
    if batsmen:
        team_text += "*Batsmen:*\n"
        for player in batsmen:
            stats = f" | Runs: {player.runs or 0}" if player.runs else ""
            team_text += (
                f"• {player.name} ({player.team}) - ₹{player.price} cr{stats}\n"
            )
        team_text += "\n"

    # Add bowlers
    if bowlers:
        team_text += "*Bowlers:*\n"
        for player in bowlers:
            stats = f" | Wickets: {player.wickets or 0}" if player.wickets else ""
            team_text += (
                f"• {player.name} ({player.team}) - ₹{player.price} cr{stats}\n"
            )
        team_text += "\n"

    # Add all-rounders
    if all_rounders:
        team_text += "*All-Rounders:*\n"
        for player in all_rounders:
            stats = ""
            if player.runs or player.wickets:
                stats = f" | Runs: {player.runs or 0}, Wickets: {player.wickets or 0}"
            team_text += (
                f"• {player.name} ({player.team}) - ₹{player.price} cr{stats}\n"
            )
        team_text += "\n"

    # Add wicket-keepers
    if wicket_keepers:
        team_text += "*Wicket-Keepers:*\n"
        for player in wicket_keepers:
            stats = f" | Runs: {player.runs or 0}" if player.runs else ""
            team_text += (
                f"• {player.name} ({player.team}) - ₹{player.price} cr{stats}\n"
            )

    # Add team management buttons
    keyboard = [
        [InlineKeyboardButton("Buy Player", callback_data="buy_player")],
        [InlineKeyboardButton("Sell Player", callback_data="sell_player")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        team_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /budget command."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You don't have an account yet. Use /start to create one."
        )
        return

    # Calculate budget details
    async with get_session() as session:
        user_id = db_user["id"]

        # Get total spent
        stmt = (
            "SELECT SUM(price) as total_spent "
            "FROM user_player_links "
            "WHERE user_id = :user_id"
        )
        result = await session.execute(stmt, {"user_id": user_id})
        row = result.fetchone()
        total_spent = row.total_spent if row and row.total_spent else 0

    # Format budget message
    budget_text = (
        f"💰 *Your Budget* 💰\n\n"
        f"Initial Budget: ₹100.0 crores\n"
        f"Total Spent: ₹{total_spent} crores\n"
        f"Remaining Budget: ₹{db_user['budget']} crores\n\n"
        f"You can use this budget to buy more players for your team."
    )

    await update.message.reply_text(budget_text, parse_mode="Markdown")


async def leaderboard_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /leaderboard command."""
    # Get top users by points
    async with get_session() as session:
        stmt = (
            "SELECT id, username, full_name, total_points "
            "FROM users "
            "ORDER BY total_points DESC "
            "LIMIT 10"
        )
        result = await session.execute(stmt)
        users = result.fetchall()

    if not users:
        await update.message.reply_text("No users found in the leaderboard yet.")
        return

    # Format leaderboard message
    leaderboard_text = "🏆 *Gully Cricket Leaderboard* 🏆\n\n"

    for i, user in enumerate(users, 1):
        leaderboard_text += (
            f"{i}. {user.full_name} (@{user.username}) - {user.total_points} points\n"
        )

    await update.message.reply_text(leaderboard_text, parse_mode="Markdown")


# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("players_page_"):
        # Handle pagination for players list
        page = int(data.split("_")[-1])

        # Update context with the new page
        if not context.user_data.get("filters"):
            context.user_data["filters"] = {}
        context.user_data["filters"]["page"] = page

        # Re-run players command with updated page
        context.args = []
        if "team" in context.user_data["filters"]:
            context.args.append(f"team={context.user_data['filters']['team']}")
        if "type" in context.user_data["filters"]:
            context.args.append(f"type={context.user_data['filters']['type']}")
        context.args.append(f"page={page+1}")

        await list_players_command(update, context)

    elif data.startswith("player_details_"):
        # Handle player details view
        player_id = int(data.split("_")[-1])

        # Get player details
        async with get_session() as session:
            player = session.get(Player, player_id)
            if not player:
                await query.edit_message_text("Player not found.")
                return

            # Get player stats
            stats = session.exec(
                select(PlayerStats).where(PlayerStats.player_id == player_id)
            ).first()

        # Format player details
        details_text = (
            f"🏏 *Player Details: {player.name}* 🏏\n\n"
            f"Team: {player.team}\n"
            f"Type: {player.player_type}\n"
            f"Base Price: ₹{player.base_price or 'N/A'} cr\n"
            f"Sold Price: ₹{player.sold_price or 'N/A'} cr\n\n"
        )

        if stats:
            details_text += (
                f"*Statistics:*\n"
                f"Matches: {stats.matches_played}\n"
                f"Runs: {stats.runs}\n"
                f"Wickets: {stats.wickets}\n"
                f"Highest Score: {stats.highest_score or 'N/A'}\n"
                f"Best Bowling: {stats.best_bowling or 'N/A'}\n"
            )
        else:
            details_text += "No statistics available for this player yet."

        # Add buy button
        keyboard = [
            [
                InlineKeyboardButton(
                    "Buy Player", callback_data=f"buy_player_{player_id}"
                )
            ],
            [InlineKeyboardButton("Back to Players", callback_data="back_to_players")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            details_text, reply_markup=reply_markup, parse_mode="Markdown"
        )

    elif data.startswith("buy_player_"):
        # Handle buy player action
        player_id = int(data.split("_")[-1])
        user = update.effective_user

        # Get user and player
        async with get_session() as session:
            db_user = session.exec(
                select(User).where(User.telegram_id == user.id)
            ).first()

            if not db_user:
                await query.edit_message_text(
                    "You don't have an account yet. Use /start to create one."
                )
                return

            player = session.get(Player, player_id)
            if not player:
                await query.edit_message_text("Player not found.")
                return

            # Check if user already has this player
            existing_link = session.exec(
                select(UserPlayer).where(
                    UserPlayer.user_id == db_user.id,
                    UserPlayer.player_id == player_id,
                )
            ).first()

            if existing_link:
                await query.edit_message_text(
                    f"You already have {player.name} in your team."
                )
                return

            # Check if user has enough budget
            price = player.sold_price or player.base_price or Decimal("1.0")
            if db_user.budget < price:
                await query.edit_message_text(
                    f"You don't have enough budget to buy {player.name}.\n"
                    f"Required: ₹{price} cr, Available: ₹{db_user.budget} cr"
                )
                return

            # Buy player
            db_user.budget -= price
            link = UserPlayer(user_id=db_user.id, player_id=player_id, price=price)
            session.add(link)
            session.commit()

        await query.edit_message_text(
            f"✅ You have successfully bought {player.name} for ₹{price} cr!\n\n"
            f"Remaining budget: ₹{db_user.budget} cr\n\n"
            f"Use /myteam to see your updated team."
        )

    elif data == "back_to_players":
        # Go back to players list
        context.args = []
        await list_players_command(update, context)


# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")

    # Send message to user if update is not None
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred. Please try again later."
        )


def main():
    """Main function to run the bot."""
    # Create the application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", start.register_command))
    application.add_handler(CommandHandler("game_guide", game_guide_command))

    # Profile commands
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("budget", budget_command))

    # Player commands
    application.add_handler(CommandHandler("players", list_players_command))
    application.add_handler(CommandHandler("search", players.search_players_command))

    # Team commands
    application.add_handler(CommandHandler("myteam", my_team_command))
    application.add_handler(CommandHandler("captain", team.set_captain_command))
    application.add_handler(CommandHandler("transfer", team.transfer_command))

    # Auction commands
    application.add_handler(CommandHandler("auction", auction.auction_status_command))
    application.add_handler(
        CommandHandler("submit_squad", auction.submit_squad_command)
    )
    application.add_handler(
        CommandHandler("round_zero_status", auction.round_zero_status_command)
    )
    application.add_handler(
        CommandHandler("vote_time_slot", auction.vote_time_slot_command)
    )
    application.add_handler(
        CommandHandler("time_slot_results", auction.time_slot_results_command)
    )

    # Admin commands
    application.add_handler(CommandHandler("admin_panel", admin_panel_command))
    application.add_handler(CommandHandler("add_admin", add_admin_command))
    application.add_handler(CommandHandler("remove_admin", remove_admin_command))
    application.add_handler(CommandHandler("nominate_admin", nominate_admin_command))
    application.add_handler(CommandHandler("gully_settings", gully_settings_command))
    application.add_handler(CommandHandler("invite_link", invite_link_command))
    application.add_handler(CommandHandler("setup_wizard", setup_wizard_command))
    application.add_handler(CommandHandler("admin_roles", admin_roles_command))

    # Register callback query handlers
    application.add_handler(
        CallbackQueryHandler(navigation.handle_navigation_callback, pattern="^nav_")
    )
    application.add_handler(
        CallbackQueryHandler(
            player_callbacks.handle_player_callback, pattern="^player_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            auction_callbacks.handle_auction_callback, pattern="^auction_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(handle_term_callback, pattern="^(term_|category_)")
    )

    # Admin callback handler
    from src.bot.callbacks.admin import handle_admin_callback

    application.add_handler(
        CallbackQueryHandler(handle_admin_callback, pattern="^admin_")
    )

    # Register game handlers
    register_game_handlers(application)

    # Error handler
    application.add_error_handler(error_handler)

    # Set up command scopes (this will be done asynchronously when the bot starts)

    # Log startup
    logger.info("Bot is running. Press Ctrl+C to stop.")

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
