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

    # Log the exact start command and args
    logger.info(f"Start command triggered by user {user.id}")
    logger.info(f"Context args: {context.args}")
    logger.info(
        f"Message text: {update.message.text if update.message else 'No message'}"
    )

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
    logger.info(f"Context args: {args}")

    if args:
        arg = args[0]
        logger.info(f"Processing arg: {arg}")

        # Try to parse the argument as a gully ID
        try:
            # First, check if it's a direct digit (gully ID)
            if arg.isdigit():
                gully_id = int(arg)
                logger.info(f"Direct gully ID found: {gully_id}")
            # If it starts with "group_", extract the group ID and try to find the gully
            elif arg.startswith("group_"):
                # This is a legacy format - we should update all deep links to use gully ID directly
                logger.warning(f"Legacy group ID format detected: {arg}")
                # For now, tell the user to use the new registration link
                await update.message.reply_text(
                    "⚠️ This registration link is outdated. Please ask the group admin to send you a new registration link."
                )
                return ConversationHandler.END
            else:
                # Unrecognized format
                logger.warning(f"Unrecognized argument format: {arg}")
                gully_id = None
        except ValueError:
            logger.error(f"Failed to parse argument as gully ID: {arg}")
            gully_id = None
    else:
        # No arguments provided
        gully_id = None

    if gully_id is not None:
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
        # Store necessary data in user_data dictionary which persists across conversation steps
        context.user_data["user_id"] = db_user["id"]
        context.user_data["gully_id"] = gully_id
        context.user_data["gully_name"] = gully["name"]

        # Also set in context manager for consistency
        ctx_manager.set_active_gully_id(context, gully_id)

        await update.message.reply_text(
            f"Welcome to Gully '{gully['name']}'!\n\n"
            f"Let's set up your fantasy team. Please enter your team name:"
        )
        return TEAM_NAME

    # No valid gully ID found, continue with the "no deep link" flow
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

    # Get user ID and gully ID from user_data (which persists across conversation steps)
    user_id = context.user_data.get("user_id")
    gully_id = context.user_data.get("gully_id")
    gully_name = context.user_data.get("gully_name")

    # Also try to get from context manager as fallback
    if not user_id:
        user_id = ctx_manager.get_user_id(context)
    if not gully_id:
        gully_id = ctx_manager.get_active_gully_id(context)

    logger.info(
        f"Registration data - user_id: {user_id}, gully_id: {gully_id}, team_name: {team_name}"
    )

    if not user_id or not gully_id:
        logger.error(
            f"Missing registration data - user_id: {user_id}, gully_id: {gully_id}"
        )
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
        "role": "member",
    }

    try:
        logger.info(f"Adding participant with data: {participant_data}")
        participant = await client.add_participant(participant_data)

        if not participant:
            logger.error("Failed to add participant - API returned None")
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
    except Exception as e:
        logger.error(f"Error adding participant: {e}")
        await update.message.reply_text(
            "⚠️ There was an error registering your team. Please try again later."
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
        logger.info("Not a new chat member event")
        return

    bot = context.bot
    bot_added = False
    for member in update.message.new_chat_members:
        if member.id == bot.id:
            bot_added = True
            break

    if not bot_added:
        logger.info("Bot was not added in this event")
        return

    # Bot was added to a group
    group = update.effective_chat
    user = update.effective_user  # User who added the bot

    logger.info(
        f"Bot was added to group {group.title} (ID: {group.id}) by user {user.first_name} (ID: {user.id})"
    )

    # Check if API is available
    if not await wait_for_api(update, context):
        logger.error("API not available when adding bot to group")
        return

    # Create a gully for this group
    client = await get_initialized_onboarding_client()

    # Check if gully already exists for this group - use the group ID as is (negative)
    try:
        existing_gully = await client.get_gully_by_telegram_group_id(group.id)

        if existing_gully:
            logger.info(f"Group already has a gully: {existing_gully['name']}")
            logger.info(
                f"Existing gully details: {existing_gully}"
            )  # Log the entire object

            # Try to get the ID, with fallbacks
            gully_id = None
            if "id" in existing_gully:
                gully_id = existing_gully["id"]
            elif "_id" in existing_gully:
                gully_id = existing_gully["_id"]

            if not gully_id:
                logger.error(f"Could not find ID in existing gully: {existing_gully}")
                await update.message.reply_text(
                    f"This group is already set as Gully '{existing_gully['name']}'."
                )
                return

            # Create deep link for registration using the existing gully ID
            bot_username = (await bot.get_me()).username
            gully_id_str = str(gully_id)
            deep_link = f"https://t.me/{bot_username}?start={gully_id_str}"

            logger.info(f"Created deep link for existing gully: {deep_link}")

            # Create inline keyboard with registration button
            keyboard = [[InlineKeyboardButton("Register to Play", url=deep_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send message with registration link
            await update.message.reply_text(
                f"This group is already set as Gully '{existing_gully['name']}'.\n\n"
                f"Click below to register and set up your team:",
                reply_markup=reply_markup,
            )
            return
    except Exception as e:
        logger.error(f"Error checking for existing gully: {e}")
        # Continue with creating a new gully

    # Create a new gully
    try:
        logger.info(f"Creating new gully for group {group.id}")

        # First, create the admin user if they don't exist
        admin_user = await client.get_user_by_telegram_id(user.id)
        if not admin_user:
            admin_user = await client.create_user(
                telegram_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )

        if not admin_user:
            logger.error("Failed to create or get admin user")
            await update.message.reply_text(
                "⚠️ There was an error setting up this group as a gully. Please try again later."
            )
            return

        # Create the gully using the API endpoint directly
        # Following the pattern from squad.py
        endpoint = "/api/gullies/"
        data = {
            "name": group.title,
            "telegram_group_id": group.id,  # Use the group ID as is (negative)
            "telegram_bot_id": bot.id,
            "admin_user_id": admin_user["id"],
        }

        logger.info(f"Creating gully with data: {data}")
        response = await client._make_request("POST", endpoint, data=data)

        if not response.get("success"):
            logger.error(f"Failed to create gully: {response.get('error')}")
            await update.message.reply_text(
                "⚠️ There was an error setting up this group as a gully. Please try again later."
            )
            return

        gully = response.get("data", {})
        logger.info(f"Successfully created gully: {gully['name']} (ID: {gully['id']})")

        # Create deep link for registration using the GULLY ID directly
        bot_username = (await bot.get_me()).username
        # Use the actual gully ID from the API response
        gully_id_str = str(gully["id"])

        # Create a direct deep link with the gully ID
        deep_link = f"https://t.me/{bot_username}?start={gully_id_str}"

        logger.info(f"Created deep link: {deep_link} for gully ID: {gully_id_str}")

        # Create inline keyboard with registration button
        keyboard = [[InlineKeyboardButton("Register to Play", url=deep_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send welcome message
        await update.message.reply_text(
            f"This group is now set as Gully '{gully['name']}'.\n\n"
            f"@{admin_user['username'] if admin_user.get('username') else user.first_name} is the admin. "
            f"Click below to register and set up your team:",
            reply_markup=reply_markup,
        )

    except Exception as e:
        logger.error(f"Error in handle_new_group: {e}")
        await update.message.reply_text(
            "⚠️ There was an error setting up this group as a gully. Please try again later."
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
        name="onboarding_conversation",
    )

    return [
        start_conv_handler,
        CommandHandler("gullies", gullies_command),
        CallbackQueryHandler(handle_gully_selection, pattern=r"^gully:"),
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_group),
    ]
