from telegram import Update
from telegram.ext import ContextTypes
from decimal import Decimal

from src.bot.bot import api_client
from src.bot.keyboards.common import get_help_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user

    # Check if user exists in our database
    db_user = await api_client.get_user(user.id)

    if db_user:
        # User already exists
        welcome_message = (
            f"Welcome back, {user.first_name}! 🏏\n\n"
            f"Your current budget: ₹{db_user['budget']} cr\n"
            f"Your total points: {db_user['total_points']}\n\n"
            f"Use /help to see available commands."
        )
    else:
        # New user, create account
        new_user = {
            "telegram_id": user.id,
            "username": user.username or f"user_{user.id}",
            "full_name": user.full_name,
            "budget": 100.0,
            "total_points": 0.0,
        }
        db_user = await api_client.create_user(new_user)

        if db_user:
            welcome_message = (
                f"Welcome to GullyGuru Fantasy Cricket, {user.first_name}! 🏏\n\n"
                f"Your account has been created successfully.\n"
                f"Starting budget: ₹{db_user['budget']} cr\n\n"
                f"Use /help to see available commands and get started!"
            )
        else:
            welcome_message = (
                f"Welcome to GullyGuru Fantasy Cricket, {user.first_name}! 🏏\n\n"
                f"There was an issue creating your account. Please try again later."
            )

    # Send welcome message with help keyboard
    keyboard = get_help_keyboard()
    await update.message.reply_text(welcome_message, reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        "*GullyGuru Fantasy Cricket Commands*\n\n"
        "*Basic Commands:*\n"
        "/start - Start the bot and register\n"
        "/help - Show this help message\n"
        "/profile - View your profile\n"
        "/budget - Check your remaining budget\n\n"
        "*Player Commands:*\n"
        "/players - Browse available players\n"
        "/search - Search for specific players\n\n"
        "*Team Commands:*\n"
        "/myteam - View your current team\n"
        "/captain - Set your team captain\n"
        "/transfer - Transfer players\n\n"
        "*Auction Commands:*\n"
        "/auction - Check auction status\n"
        "/bid - Place a bid\n\n"
        "*Match Commands:*\n"
        "/matches - View upcoming matches\n"
        "/predict - Predict match outcomes\n"
        "/live - Check live match scores\n\n"
        "*Leaderboard Commands:*\n"
        "/leaderboard - View global rankings\n"
        "/points - Check your points\n\n"
    )

    keyboard = get_help_keyboard()
    await update.message.reply_text(
        help_text, parse_mode="Markdown", reply_markup=keyboard
    )


async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /register command."""
    user = update.effective_user

    # Check if user already exists
    db_user = await api_client.get_user(user.id)

    if db_user:
        await update.message.reply_text(
            f"You are already registered, {user.first_name}!\n\n"
            f"Your current budget: ₹{db_user['budget']} cr\n"
            f"Your total points: {db_user['total_points']}"
        )
        return

    # Create new user
    new_user = {
        "telegram_id": user.id,
        "username": user.username or f"user_{user.id}",
        "full_name": user.full_name,
        "budget": 100.0,
        "total_points": 0.0,
    }

    db_user = await api_client.create_user(new_user)

    if db_user:
        await update.message.reply_text(
            f"Registration successful, {user.first_name}! 🎉\n\n"
            f"Starting budget: ₹{db_user['budget']} cr\n\n"
            f"Use /help to see available commands and get started!"
        )
    else:
        await update.message.reply_text("Registration failed. Please try again later.")
