"""
Handlers for the /start and /help commands.
These are the entry points for new users and provide basic guidance.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.api_client_instance import api_client
from src.bot.utils.user_management import (
    ensure_user_exists,
    ensure_user_in_gully,
    get_active_gully,
)

# Conversation states
# NAME_INPUT = 1  # No longer needed

# Configure logging
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /start command.
    This is the entry point for new users.

    In private chats: Initiates the registration process for the individual user.
    In group chats: Checks all group members and prompts unregistered users to start the bot.
    """
    # Get the chat type
    chat_type = update.effective_chat.type

    # Handle group chat scenario
    if chat_type in ["group", "supergroup"]:
        return await handle_group_start(update, context)

    # Handle private chat scenario
    user = update.effective_user

    # Check if this is a deep link from a group invitation
    args = context.args
    from_group = None
    if args and args[0].startswith("from_group_"):
        try:
            from_group = int(args[0].split("_")[2])
            logger.info(f"User {user.id} starting from group {from_group}")
        except (IndexError, ValueError) as e:
            logger.error(f"Error parsing from_group parameter: {e}")

    # Ensure user exists in database
    db_user = await ensure_user_exists(user)
    if not db_user:
        # User creation failed
        logger.error(f"Failed to create user {user.id} in database")
        await update.message.reply_text(
            "Sorry, there was an error registering your account. Please try again later."
        )
        return ConversationHandler.END

    # Check if this is a new user (just created) or an existing user
    is_new_user = db_user.get("created_at") == db_user.get("updated_at")

    # If from a group, check if user is already in the gully
    if from_group:
        gully = await api_client.get_gully_by_chat_id(from_group)
        if gully:
            gully_id = gully.get("id")
            gully_name = gully.get("name")

            # Check if user is already in the gully
            participant = await api_client.get_user_gully_participation(
                db_user["id"], gully_id
            )

            if participant:
                # User is already in the gully
                await update.message.reply_text(
                    f"You're already registered in *{gully_name}* as *{participant.get('team_name')}*.",
                    parse_mode="Markdown",
                )

                # Set this as the user's active gully if it's not already
                if not participant.get("is_active"):
                    await api_client.set_active_gully(participant["id"])
                    await update.message.reply_text(
                        "I've set this as your active gully."
                    )
            else:
                # User is not in the gully, ask if they want to join
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Yes, join this gully",
                            callback_data=f"join_gully_{gully_id}",
                        ),
                        InlineKeyboardButton(
                            "No, thanks", callback_data="decline_gully"
                        ),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    f"You're not yet a participant in the *{gully_name}* gully. Would you like to join?",
                    parse_mode="Markdown",
                    reply_markup=reply_markup,
                )
                return ConversationHandler.END

    # Welcome message
    if is_new_user:
        greeting = f"Hello {db_user.get('full_name')}! Welcome to GullyGuru. "
        await update.message.reply_text(
            f"{greeting}"
            "You are now registered as a player! 🎉\n\n"
            "You can now participate in cricket fantasy gaming with GullyGuru."
        )
    else:
        # Welcome back message for existing users
        await update.message.reply_text(
            f"Welcome back, {db_user.get('full_name')}! 👋\n\n"
            "You're already registered with GullyGuru."
        )

    # Get active gully
    active_gully = await get_active_gully(db_user["id"])
    if active_gully:
        await update.message.reply_text(
            f"Your active gully is: *{active_gully.get('name')}*",
            parse_mode="Markdown",
        )

        # Check if user has a squad and prompt accordingly
        squad = await api_client.get_user_squad_submission(user.id)
        if not squad:
            # Prompt user to submit squad with clear instructions
            await update.message.reply_text(
                "📋 *Next Step: Submit Your Initial Squad*\n\n"
                "To participate in the game, you need to select your initial team of 18 players (Round 0).\n\n"
                "Use the /submit_squad command to start building your team.",
                parse_mode="Markdown",
            )

            # Add a keyboard button for easy access to submit_squad
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Submit My Squad", callback_data="start_submit_squad"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Click the button below to start:", reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            "You don't have an active gully set. Join a group to participate in a gully."
        )

    return ConversationHandler.END


async def handle_group_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /start command in a group chat.
    This creates or retrieves the gully for the group and registers all members.
    """
    chat = update.effective_chat
    user = update.effective_user
    chat_id = chat.id

    # Log the start command in a group
    logger.info(
        f"Start command received in group {chat.title} (ID: {chat_id}) from user {user.id}"
    )

    # Check if a gully exists for this group
    gully = await api_client.get_gully_by_chat_id(chat_id)

    if not gully:
        # No gully exists, create one
        await update.message.reply_text(
            "🏏 Welcome to GullyGuru! I'll help you set up a new fantasy cricket league for this group."
        )

        # Create a new gully with default settings
        gully_name = chat.title or f"Gully_{chat_id}"
        try:
            # Use current date + 6 months for end date (placeholder)
            from datetime import datetime, timedelta

            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")

            gully = await api_client.create_gully(
                name=gully_name,
                telegram_group_id=chat_id,
                start_date=start_date,
                end_date=end_date,
            )

            if not gully or not gully.get("id"):
                await update.message.reply_text(
                    "❌ Sorry, I couldn't create a new gully. Please try again later."
                )
                return ConversationHandler.END

            await update.message.reply_text(
                f"✅ Successfully created a new gully: *{gully_name}*",
                parse_mode="Markdown",
            )

            # Make the command sender an admin
            db_user = await ensure_user_exists(user)
            if db_user:
                # Add user to gully and make them an admin
                participant = await ensure_user_in_gully(db_user["id"], gully["id"])
                if participant:
                    await api_client.update_gully_participant_role(
                        participant["id"], "admin"
                    )
                    logger.info(f"Made user {user.id} an admin of gully {gully['id']}")

                    # Set this as the user's active gully
                    await api_client.set_active_gully(participant["id"])

        except Exception as e:
            logger.error(f"Error creating gully: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error setting up the gully. Please try again later."
            )
            return ConversationHandler.END
    else:
        # Gully exists, welcome the user
        await update.message.reply_text(
            f"🏏 Welcome to the *{gully.get('name')}* fantasy cricket league!",
            parse_mode="Markdown",
        )

        # Auto-register the user who triggered the command
        db_user = await ensure_user_exists(user)
        if not db_user:
            await update.message.reply_text(
                "❌ Sorry, there was an error registering your account. Please try again later."
            )
            return ConversationHandler.END

        # Check if user is already part of the gully
        participant = await api_client.get_user_gully_participation(
            db_user["id"], gully["id"]
        )

        if participant:
            # User is already in the gully
            await update.message.reply_text(
                f"You're already registered in this gully as *{participant.get('team_name')}*.",
                parse_mode="Markdown",
            )

            # Set this as the user's active gully if it's not already
            if not participant.get("is_active"):
                await api_client.set_active_gully(participant["id"])
                await update.message.reply_text("I've set this as your active gully.")
        else:
            # User is not in the gully, ask if they want to join
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Yes, join this gully",
                        callback_data=f"join_gully_{gully['id']}",
                    ),
                    InlineKeyboardButton("No, thanks", callback_data="decline_gully"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"You're not yet a participant in the *{gully.get('name')}* gully. Would you like to join?",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

    # Add a button to check registration status
    keyboard = [
        [
            InlineKeyboardButton(
                "Check Registration Status", callback_data="check_members"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👥 Group admins can check which members have registered:",
        reply_markup=reply_markup,
    )

    return ConversationHandler.END


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
            "/start - Register to play\n"
            "/auction_status - Check auction status for all rounds\n\n"
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
            "No gully has been set up for this group yet. Use /start to create one."
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

    # Get all users
    users = {}
    for participant in participants:
        user_id = participant["user_id"]
        user = await api_client.get_user_by_id(user_id)
        if user:
            users[user_id] = user

    # Check each chat member
    for member in chat_members:
        user_found = False
        for user_id, user in users.items():
            if user.get("telegram_id") == member.user.id:
                registered_members.append(
                    f"✅ @{member.user.username or user.get('full_name')}"
                )
                user_found = True
                break

        if not user_found:
            unregistered_members.append(
                f"❌ @{member.user.username or member.user.first_name}"
            )

    # Build the response message
    message = f"*Registration Status for {gully.get('name')}*\n\n"

    if registered_members:
        message += "*Registered Members:*\n"
        message += "\n".join(registered_members)
        message += "\n\n"

    if unregistered_members:
        message += "*Unregistered Members:*\n"
        message += "\n".join(unregistered_members)
        message += "\n\n"

        # Add instructions for unregistered members
        bot_username = context.bot.username
        deep_link = f"https://t.me/{bot_username}?start=from_group_{chat.id}"
        message += f"Unregistered members can [click here]({deep_link}) to register."

    await update.message.reply_text(
        message, parse_mode="Markdown", disable_web_page_preview=True
    )


async def handle_start_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callbacks from the start command."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == "start_submit_squad":
        # Redirect to submit_squad command
        await query.edit_message_text("Redirecting to squad submission...")

        # Import the submit_squad command
        from src.bot.handlers.team import submit_squad_command

        # Create a new update object with the text "/submit_squad"
        new_message = query.message.copy()
        new_message.text = "/submit_squad"
        new_update = Update(
            update_id=update.update_id,
            message=new_message,
            callback_query=None,
        )

        # Call the submit_squad command
        await submit_squad_command(new_update, context)

    elif callback_data == "check_members":
        # Check which members have registered
        await query.edit_message_text("Checking registered members...")

        # Create a new update object with the text "/check_members"
        new_message = query.message.copy()
        new_message.text = "/check_members"
        new_update = Update(
            update_id=update.update_id,
            message=new_message,
            callback_query=None,
        )

        # Call the check_members command
        await check_members_command(new_update, context)

    elif callback_data.startswith("join_gully_"):
        # Extract gully ID from callback data
        try:
            gully_id = int(callback_data.split("_")[2])
            user = update.effective_user

            # Get user from database
            db_user = await ensure_user_exists(user)
            if not db_user:
                await query.edit_message_text(
                    "❌ Sorry, there was an error with your account. Please try again later."
                )
                return

            # Add user to gully
            participant = await ensure_user_in_gully(db_user["id"], gully_id)
            if not participant:
                await query.edit_message_text(
                    "❌ Sorry, there was an error adding you to the gully. Please try again later."
                )
                return

            # Set this as the user's active gully
            await api_client.set_active_gully(participant["id"])

            # Get gully details
            gully = await api_client.get_gully(gully_id)
            gully_name = gully.get("name", "this gully") if gully else "this gully"

            # Confirm joining
            await query.edit_message_text(
                f"✅ You've successfully joined *{gully_name}* as *{participant.get('team_name')}*!\n\n"
                f"This is now your active gully. You can use /myteam to view your team or "
                f"/submit_squad to build your initial squad.",
                parse_mode="Markdown",
            )

        except (IndexError, ValueError) as e:
            logger.error(f"Error parsing join_gully callback data: {e}")
            await query.edit_message_text(
                "❌ Sorry, there was an error processing your request. Please try again later."
            )

    elif callback_data == "decline_gully":
        # User declined to join the gully
        await query.edit_message_text(
            "You've chosen not to join this gully. You can always join later by using the /start command again."
        )

    else:
        await query.message.reply_text(
            "Unknown callback. Please try again or use /help for available commands."
        )


def get_start_conversation_handler():
    """Return a conversation handler for the start command."""
    from telegram.ext import (
        ConversationHandler,
        CommandHandler,
    )

    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            # We no longer need the NAME_INPUT state
        },
        fallbacks=[CommandHandler("start", start_command)],
    )
