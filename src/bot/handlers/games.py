from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import pytz

from src.bot.bot import api_client
from src.bot.keyboards.gullies import (
    get_gully_management_keyboard,
    get_gully_list_keyboard,
)

# Conversation states
GULLY_NAME = 1
TEAM_NAME = 1
GULLY_SELECTION = 1

logger = logging.getLogger(__name__)


async def create_gully_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Start the process of creating a new gully."""
    # Check if command is used in a group
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "This command can only be used in a group chat. Please add me to a group and try again."
        )
        return ConversationHandler.END

    # Check if user is an admin in the group
    chat_member = await context.bot.get_chat_member(
        chat_id=update.effective_chat.id, user_id=update.effective_user.id
    )

    if chat_member.status not in ["creator", "administrator"]:
        await update.message.reply_text("Only group administrators can create gullies.")
        return ConversationHandler.END

    # Check if group already has a gully
    existing_gully = await api_client.get_gully_by_group(update.effective_chat.id)

    if existing_gully:
        await update.message.reply_text(
            f"This group already has a gully: *{existing_gully.get('name')}*\n"
            f"Status: {existing_gully.get('status')}\n\n"
            f"You cannot create another gully in this group.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Let's create a new fantasy cricket gully for this group!\n\n"
        "Please enter a name for your gully:"
    )

    return GULLY_NAME


async def gully_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle gully name input."""
    gully_name = update.message.text.strip()

    if len(gully_name) < 3 or len(gully_name) > 50:
        await update.message.reply_text(
            "Gully name must be between 3 and 50 characters. Please try again:"
        )
        return GULLY_NAME

    # Store gully name in context
    context.user_data["gully_name"] = gully_name

    # Calculate default dates (12 weeks from now)
    now = datetime.now(pytz.UTC)
    start_date = now
    end_date = now + timedelta(weeks=12)

    # Create gully
    result = await api_client.create_gully(
        name=gully_name,
        telegram_group_id=update.effective_chat.id,
        start_date=start_date,
        end_date=end_date,
    )

    if not result or "id" not in result:
        await update.message.reply_text(
            f"Failed to create gully: {result.get('error', 'Unknown error')}"
        )
        return ConversationHandler.END

    # Store gully ID in context
    context.chat_data["gully_id"] = result.get("id")

    # Announce gully creation
    await update.message.reply_text(
        f"🎮 *New Fantasy Cricket Gully Created!* 🎮\n\n"
        f"*{gully_name}* has been created successfully!\n\n"
        f"Group members can now join this gully by using the /join_gully command.\n\n"
        f"The season will run for 12 weeks, ending on {end_date.strftime('%d %b %Y')}.",
        parse_mode="Markdown",
    )

    return ConversationHandler.END


async def join_gully_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the process of joining a gully."""
    user = update.effective_user

    # Check if command is used in a group
    if update.effective_chat.type in ["group", "supergroup"]:
        # Get gully for this group
        gully = await api_client.get_gully_by_group(update.effective_chat.id)

        if not gully:
            await update.message.reply_text(
                "There is no active gully in this group. Ask an admin to create one with /create_gully."
            )
            return ConversationHandler.END

        # Store gully ID in context
        context.user_data["joining_gully_id"] = gully.get("id")
        context.user_data["joining_gully_name"] = gully.get("name")

        # Check if user is already in this gully
        participants = await api_client.get_gully_participants(gully.get("id"))

        for participant in participants:
            if participant.get("user_id") == user.id:
                await update.message.reply_text(
                    f"You are already participating in *{gully.get('name')}* with team *{participant.get('team_name')}*.",
                    parse_mode="Markdown",
                )
                return ConversationHandler.END

        # Ask for team name
        await update.message.reply_text(
            f"You are joining *{gully.get('name')}*!\n\n"
            f"Please enter a name for your team:",
            parse_mode="Markdown",
        )

        return TEAM_NAME
    else:
        # In private chat, show list of available gullies
        db_user = await api_client.get_user(user.id)

        if not db_user:
            await update.message.reply_text(
                "You need to register first. Use /start to register."
            )
            return ConversationHandler.END

        # Get user's gullies
        user_gullies = await api_client.get_user_gullies(db_user.get("id"))

        if not user_gullies:
            await update.message.reply_text(
                "You are not participating in any gullies yet.\n\n"
                "Please use this command in a group chat to join a gully."
            )
            return ConversationHandler.END

        # Show list of gullies
        keyboard = get_gully_list_keyboard(user_gullies)

        await update.message.reply_text(
            "You are participating in the following gullies:", reply_markup=keyboard
        )

        return ConversationHandler.END


async def team_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle team name input."""
    team_name = update.message.text.strip()

    if len(team_name) < 3 or len(team_name) > 30:
        await update.message.reply_text(
            "Team name must be between 3 and 30 characters. Please try again:"
        )
        return TEAM_NAME

    user = update.effective_user
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return ConversationHandler.END

    # Join gully
    gully_id = context.user_data.get("joining_gully_id")
    gully_name = context.user_data.get("joining_gully_name")

    result = await api_client.join_gully(
        gully_id=gully_id, user_id=db_user.get("id"), team_name=team_name
    )

    if not result or "id" not in result:
        await update.message.reply_text(
            f"Failed to join gully: {result.get('error', 'Unknown error')}"
        )
        return ConversationHandler.END

    # Announce joining
    await update.message.reply_text(
        f"🎉 You have successfully joined *{gully_name}* with team *{team_name}*!\n\n"
        f"Your starting budget is ₹100 cr.\n\n"
        f"Use /myteam to manage your team and /auction to participate in player auctions.",
        parse_mode="Markdown",
    )

    # Announce in group if command was used in group
    if update.effective_chat.type in ["group", "supergroup"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"�� *{user.username or user.first_name}* has joined the gully with team *{team_name}*!",
            parse_mode="Markdown",
        )

    return ConversationHandler.END


async def my_gullies_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show list of gullies the user is participating in."""
    user = update.effective_user
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get user's gullies
    user_gullies = await api_client.get_user_gullies(db_user.get("id"))

    if not user_gullies:
        await update.message.reply_text(
            "You are not participating in any gullies yet.\n\n"
            "Use /join_gully in a group chat to join a gully."
        )
        return

    # Show list of gullies
    keyboard = get_gully_list_keyboard(user_gullies)

    await update.message.reply_text(
        "You are participating in the following gullies:", reply_markup=keyboard
    )


async def switch_gully_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Start the process of switching active gully context."""
    user = update.effective_user
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return ConversationHandler.END

    # Get user's gullies
    user_gullies = await api_client.get_user_gullies(db_user.get("id"))

    if not user_gullies:
        await update.message.reply_text(
            "You are not participating in any gullies yet.\n\n"
            "Use /join_gully in a group chat to join a gully."
        )
        return ConversationHandler.END

    # Show list of gullies for selection
    keyboard = []

    for gully in user_gullies:
        keyboard.append(
            [
                InlineKeyboardButton(
                    gully.get("name"), callback_data=f"switch_gully_{gully.get('id')}"
                )
            ]
        )

    await update.message.reply_text(
        "Select a gully to switch to:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return GULLY_SELECTION


async def gully_selection_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle gully selection for switching."""
    query = update.callback_query
    await query.answer()

    data = query.data
    gully_id = int(data.split("_")[-1])

    # Get gully details
    user_gullies = await api_client.get_user_gullies(update.effective_user.id)
    selected_gully = None

    for gully in user_gullies:
        if gully.get("id") == gully_id:
            selected_gully = gully
            break

    if not selected_gully:
        await query.edit_message_text("Gully not found. Please try again.")
        return ConversationHandler.END

    # Set active gully in user context
    context.user_data["active_gully_id"] = gully_id
    context.user_data["active_gully_name"] = selected_gully.get("name")

    await query.edit_message_text(
        f"You have switched to gully: *{selected_gully.get('name')}*\n\n"
        f"All your commands will now apply to this gully context.",
        parse_mode="Markdown",
    )

    return ConversationHandler.END


async def gully_info_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show information about the current gully."""
    # If in group, get that group's gully
    if update.effective_chat.type in ["group", "supergroup"]:
        gully = await api_client.get_gully_by_group(update.effective_chat.id)

        if not gully:
            await update.message.reply_text(
                "There is no active gully in this group. Ask an admin to create one with /create_gully."
            )
            return
    else:
        # In private chat, use active gully from context
        active_gully_id = context.user_data.get("active_gully_id")

        if not active_gully_id:
            await update.message.reply_text(
                "You don't have an active gully selected. Use /my_gullies to see your gullies."
            )
            return

        # Get gully details
        user_gullies = await api_client.get_user_gullies(update.effective_user.id)
        gully = None

        for g in user_gullies:
            if g.get("id") == active_gully_id:
                gully = g
                break

        if not gully:
            await update.message.reply_text(
                "Gully not found. Please use /my_gullies to see your available gullies."
            )
            return

    # Get participants
    participants = await api_client.get_gully_participants(gully.get("id"))

    # Format gully info
    start_date = datetime.fromisoformat(gully.get("start_date").replace("Z", "+00:00"))
    end_date = datetime.fromisoformat(gully.get("end_date").replace("Z", "+00:00"))

    message = (
        f"🎮 *{gully.get('name')}* 🎮\n\n"
        f"*Status:* {gully.get('status')}\n"
        f"*Start Date:* {start_date.strftime('%d %b %Y')}\n"
        f"*End Date:* {end_date.strftime('%d %b %Y')}\n"
        f"*Participants:* {len(participants)}\n\n"
    )

    if participants:
        message += "*Teams:*\n"
        for i, participant in enumerate(participants, 1):
            message += f"{i}. {participant.get('team_name')} (₹{participant.get('budget')} cr)\n"

    # Add keyboard for management options
    keyboard = get_gully_management_keyboard(gully.get("id"))

    await update.message.reply_text(
        message, parse_mode="Markdown", reply_markup=keyboard
    )


def register_handlers(application):
    """Register gully management handlers."""
    # Create gully conversation
    create_gully_conv = ConversationHandler(
        entry_points=[CommandHandler("create_gully", create_gully_command)],
        states={
            GULLY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gully_name_handler)
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # Join gully conversation
    join_gully_conv = ConversationHandler(
        entry_points=[CommandHandler("join_gully", join_gully_command)],
        states={
            TEAM_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, team_name_handler)
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # Switch gully conversation
    switch_gully_conv = ConversationHandler(
        entry_points=[CommandHandler("switch_gully", switch_gully_command)],
        states={
            GULLY_SELECTION: [
                CallbackQueryHandler(
                    gully_selection_handler, pattern=r"^switch_gully_\d+$"
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    application.add_handler(create_gully_conv)
    application.add_handler(join_gully_conv)
    application.add_handler(switch_gully_conv)
    application.add_handler(CommandHandler("my_gullies", my_gullies_command))
    application.add_handler(CommandHandler("gully_info", gully_info_command))
