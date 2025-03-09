"""
Handlers for the /help and /check_members commands.
These provide basic guidance and utility functions.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.api.api_client_instance import api_client

# Configure logging
logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    Provides information about available commands and how to use them.
    """
    chat_type = update.effective_chat.type

    if chat_type == "private":
        # Private chat help
        help_text = (
            "🏏 *GullyGuru Bot Help* 🏏\n\n"
            "*Available Commands:*\n"
            "/game_guide - Learn about cricket terminology and game concepts\n"
            "/myteam - View your current team composition\n"
            "/submit_squad - Submit your initial squad of 18 players (Round 0)\n"
            "/bid <amount> - Place a bid during an active auction\n"
            "/auction_status - Check the current auction status\n\n"
            "For more detailed help on any command, use /game_guide"
        )
    else:
        # Group chat help
        help_text = (
            "🏏 *GullyGuru Bot Help* 🏏\n\n"
            "*Available Group Commands:*\n"
            "/join_gully - Join this gully and start playing\n"
            "/auction_status - Check auction status for all rounds\n"
            "/check_members - See who has joined the gully\n"
            "/prompt_members - (Admin only) Prompt unregistered members to join\n\n"
            "For more commands and detailed help, message me privately."
        )

    # Add button to open private chat if in group
    if chat_type != "private":
        deep_link = f"https://t.me/{context.bot.username}?start=help"
        keyboard = [[InlineKeyboardButton("Message me privately", url=deep_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            help_text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")


async def check_members_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Check which members of the group have registered with the bot.
    This command is only available in group chats.
    """
    chat = update.effective_chat

    # Only allow in group chats
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in group chats.")
        return

    # Get the gully for this group
    gully = await api_client.get_gully_by_chat_id(chat.id)
    if not gully:
        await update.message.reply_text(
            "No gully has been set up for this group yet. Use /join_gully to join."
        )
        return

    # Get all participants in this gully
    participants = await api_client.get_gully_participants(gully["id"])

    if not participants:
        await update.message.reply_text(
            "No members have registered for this gully yet."
        )
        return

    # Get all chat members
    try:
        chat_members = []
        async for member in context.bot.get_chat_members(chat.id):
            if not member.user.is_bot:
                chat_members.append(member)
    except Exception as e:
        logger.error(f"Error getting chat members: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't retrieve the list of chat members."
        )
        return

    # Check which chat members are registered
    registered_members = []
    unregistered_members = []

    # Create a map of telegram_id to participant for quick lookup
    participant_map = {p["telegram_id"]: p for p in participants}

    for member in chat_members:
        if member.user.id in participant_map:
            registered_members.append(member.user)
        else:
            unregistered_members.append(member.user)

    # Prepare the response message
    response = f"*Gully: {gully['name']}*\n\n"

    if registered_members:
        response += "*Registered Members:*\n"
        for user in registered_members:
            name = user.full_name
            response += f"✅ {name}\n"
    else:
        response += "*No registered members yet.*\n"

    if unregistered_members:
        response += "\n*Unregistered Members:*\n"
        for user in unregistered_members:
            name = user.full_name
            response += f"❌ {name}\n"

        # Add a button for unregistered users to start the bot
        bot_username = context.bot.username
        deep_link = f"https://t.me/{bot_username}?start=from_group_{chat.id}"
        keyboard = [[InlineKeyboardButton("Join Gully", url=deep_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            response, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(response, parse_mode="Markdown")
