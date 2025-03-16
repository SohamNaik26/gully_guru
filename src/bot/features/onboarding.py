"""
Onboarding features for the GullyGuru bot.
Handles user registration, gully creation, and team setup.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List, Union
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode

# Use the centralized client initialization
from src.bot.api_client.init import (
    get_initialized_onboarding_client,
    wait_for_api as global_wait_for_api,
)
from src.bot.context import manager as ctx_manager

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
TEAM_NAME = 1

# Callback data
REGISTER_CALLBACK = "register"


async def wait_for_api(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if API is available for the current request.

    Args:
        update: Telegram update
        context: Conversation context

    Returns:
        bool: True if API is available, False otherwise
    """
    try:
        client = await get_initialized_onboarding_client()
        if client is None:
            raise Exception("Failed to initialize onboarding client")
        return True
    except Exception as e:
        logger.error(f"API not available: {e}")
        await update.message.reply_text(
            "⚠️ The GullyGuru service is currently unavailable. Please try again later."
        )
        return False


async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """
    Handle the /start command.

    This is the entry point for new users. It checks if they're coming from a deep link,
    and if so, registers them for the corresponding gully.

    Args:
        update: Telegram update
        context: Conversation context

    Returns:
        Next conversation state or None
    """
    user = update.effective_user

    # Check if API is available
    if not await wait_for_api(update, context):
        return ConversationHandler.END

    # Get the client
    client = await get_initialized_onboarding_client()

    # Check if user exists in the database
    db_user = await client.get_user_by_telegram_id(user.id)

    # If user doesn't exist, create them
    if not db_user:
        logger.info(f"Creating new user for {user.first_name} (ID: {user.id})")
        db_user = await client.create_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

        if not db_user:
            await update.message.reply_text(
                "⚠️ There was an error creating your account. Please try again later."
            )
            return ConversationHandler.END

    # Store user ID in context
    ctx_manager.set_user_id(context, db_user["id"])

    # Check if this is a deep link with a gully ID
    args = context.args
    if args and args[0].isdigit():
        gully_id = int(args[0])
        logger.info(f"Deep link detected with gully_id: {gully_id}")

        # Get the gully
        gully = await client.get_gully(gully_id)
        if not gully:
            await update.message.reply_text(
                "⚠️ The gully you're trying to join doesn't exist or has been deleted."
            )
            return ConversationHandler.END

        # Check if user is already a participant in this gully
        participant = await client.get_participant_by_user_and_gully(
            user_id=db_user["id"], gully_id=gully_id
        )

        if participant:
            # User is already a participant, set as active gully
            ctx_manager.set_active_gully_id(context, gully_id)
            ctx_manager.set_participant_id(context, participant["id"])

            await update.message.reply_text(
                f"Welcome back to Gully '{gully['name']}'!\n\n"
                f"Your team: {participant['team_name']}\n\n"
                f"🏏 Use /squad to manage your squad\n"
                f"🎟️ Use /gullies to switch gullies"
            )
            return ConversationHandler.END

        # User is not a participant, ask for team name
        ctx_manager.set_active_gully_id(context, gully_id)

        await update.message.reply_text(
            f"Welcome to Gully '{gully['name']}'!\n\n"
            f"Let's set up your fantasy team. Please enter your team name:"
        )
        return TEAM_NAME

    # No deep link, check if user has any gullies
    user_gullies = await client.get_user_gullies(db_user["id"])

    if user_gullies:
        # User has gullies, show them
        await update.message.reply_text(
            f"Welcome back, {user.first_name}!\n\n"
            f"You have {len(user_gullies)} gullies. Use /gullies to view and select them."
        )
        return ConversationHandler.END

    # User has no gullies, show instructions
    await update.message.reply_text(
        f"Welcome to GullyGuru, {user.first_name}!\n\n"
        f"To start playing, you need to join a gully. Ask your friends to add you to their gully "
        f"or create a new one by adding this bot to a Telegram group."
    )
    return ConversationHandler.END


async def handle_team_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the team name input during registration.

    Args:
        update: Telegram update
        context: Conversation context

    Returns:
        Next conversation state
    """
    team_name = update.message.text.strip()

    if not team_name:
        await update.message.reply_text("Please enter a valid team name:")
        return TEAM_NAME

    # Store team name in context
    ctx_manager.set_team_name(context, team_name)

    # Get user ID and gully ID from context
    user_id = ctx_manager.get_user_id(context)
    gully_id = ctx_manager.get_active_gully_id(context)

    if not user_id or not gully_id:
        await update.message.reply_text(
            "⚠️ There was an error with your registration. Please try again with /start."
        )
        return ConversationHandler.END

    # Add user as participant to the gully
    client = await get_initialized_onboarding_client()
    participant_data = {
        "user_id": user_id,
        "gully_id": gully_id,
        "team_name": team_name,
        "role": "player",
    }

    participant = await client.add_participant(participant_data)

    if not participant:
        await update.message.reply_text(
            "⚠️ There was an error registering your team. Please try again later."
        )
        return ConversationHandler.END

    # Store participant ID in context
    ctx_manager.set_participant_id(context, participant["id"])

    # Registration successful
    await update.message.reply_text(
        f"Team '{team_name}' created successfully!\n\n"
        f"🏏 /squad - Manage your squad\n"
        f"🎟️ /gullies - Switch Gully\n\n"
        f"Let's start by setting up your squad. Use /squad to select your players."
    )

    return ConversationHandler.END


async def handle_new_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle when the bot is added to a new group.

    Args:
        update: Telegram update
        context: Conversation context
    """
    # Check if this is a new chat member event and the bot was added
    if not update.message or not update.message.new_chat_members:
        return

    bot = context.bot
    if not any(member.id == bot.id for member in update.message.new_chat_members):
        return

    # Bot was added to a group
    group = update.effective_chat
    user = update.effective_user  # User who added the bot

    logger.info(
        f"Bot was added to group {group.title} (ID: {group.id}) by user {user.first_name} (ID: {user.id})"
    )

    # Check if API is available
    if not await wait_for_api(update, context):
        return

    # Create a gully for this group
    client = await get_initialized_onboarding_client()

    # Check if gully already exists for this group
    existing_gully = await client.get_gully_by_telegram_group_id(group.id)

    if existing_gully:
        await update.message.reply_text(
            f"This group is already set as Gully '{existing_gully['name']}'."
        )
        return

    # Create a new gully
    result = await client.handle_complete_onboarding(
        bot_id=bot.id,
        group_id=group.id,
        group_name=group.title,
        admin_telegram_id=user.id,
        admin_first_name=user.first_name,
        admin_username=user.username,
        admin_last_name=user.last_name,
    )

    if not result["success"]:
        await update.message.reply_text(
            "⚠️ There was an error setting up this group as a gully. Please try again later."
        )
        return

    gully = result["gully"]
    admin_user = result["admin_user"]

    # Create deep link for registration
    bot_username = (await bot.get_me()).username
    deep_link = f"https://t.me/{bot_username}?start={gully['id']}"

    # Create inline keyboard with registration button
    keyboard = [[InlineKeyboardButton("Register to Play", url=deep_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send welcome message
    await update.message.reply_text(
        f"This group is now set as Gully '{gully['name']}'.\n\n"
        f"@{admin_user['username'] if admin_user.get('username') else user.first_name} is the admin. "
        f"Click below to register and set up your team.",
        reply_markup=reply_markup,
    )


async def gullies_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /gullies command.

    Shows a list of gullies the user is part of and allows them to select one.

    Args:
        update: Telegram update
        context: Conversation context
    """
    user = update.effective_user

    # Check if API is available
    if not await wait_for_api(update, context):
        return

    # Get user ID from context or fetch from API
    user_id = ctx_manager.get_user_id(context)
    if not user_id:
        client = await get_initialized_onboarding_client()
        db_user = await client.get_user_by_telegram_id(user.id)

        if not db_user:
            await update.message.reply_text(
                "⚠️ Your account was not found. Please use /start to register."
            )
            return

        user_id = db_user["id"]
        ctx_manager.set_user_id(context, user_id)

    # Get user's gullies
    client = await get_initialized_onboarding_client()
    user_gullies = await client.get_user_gullies(user_id)

    if not user_gullies:
        await update.message.reply_text(
            "You are not part of any gullies yet. Ask your friends to add you to their gully "
            "or create a new one by adding this bot to a Telegram group."
        )
        return

    # Create inline keyboard with gullies
    keyboard = []
    for gully in user_gullies:
        # Get participant info
        participant = await client.get_participant_by_user_and_gully(
            user_id=user_id, gully_id=gully["id"]
        )

        if participant:
            team_name = participant["team_name"]
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{gully['name']} ({team_name})",
                        callback_data=f"gully:{gully['id']}:{participant['id']}",
                    )
                ]
            )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select a gully to activate:", reply_markup=reply_markup
    )


async def handle_gully_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle gully selection from the inline keyboard.

    Args:
        update: Telegram update
        context: Conversation context
    """
    query = update.callback_query
    await query.answer()

    # Parse callback data
    data = query.data.split(":")
    if len(data) != 3 or data[0] != "gully":
        await query.edit_message_text(
            "⚠️ Invalid selection. Please try again with /gullies."
        )
        return

    gully_id = int(data[1])
    participant_id = int(data[2])

    # Store in context
    ctx_manager.set_active_gully_id(context, gully_id)
    ctx_manager.set_participant_id(context, participant_id)

    # Get gully details
    client = await get_initialized_onboarding_client()
    gully = await client.get_gully(gully_id)

    if not gully:
        await query.edit_message_text(
            "⚠️ The selected gully doesn't exist or has been deleted. Please try again with /gullies."
        )
        return

    # Get participant details
    participant = await client.get_participant_by_user_and_gully(
        user_id=ctx_manager.get_user_id(context), gully_id=gully_id
    )

    if not participant:
        await query.edit_message_text(
            "⚠️ You are no longer a participant in this gully. Please try again with /gullies."
        )
        return

    await query.edit_message_text(
        f"Gully '{gully['name']}' activated!\n\n"
        f"Your team: {participant['team_name']}\n\n"
        f"🏏 Use /squad to manage your squad"
    )


def get_handlers():
    """
    Get all handlers for onboarding features.

    Returns:
        List of handlers
    """
    start_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            TEAM_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_team_name)
            ]
        },
        fallbacks=[CommandHandler("start", start_command)],
    )

    return [
        start_conv_handler,
        CommandHandler("gullies", gullies_command),
        CallbackQueryHandler(handle_gully_selection, pattern=r"^gully:"),
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_group),
    ]
