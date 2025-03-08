"""
Handlers for the /start and /help commands.
These are the entry points for new users and provide basic guidance.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.api_client_instance import api_client
from src.bot.utils.user_management import ensure_user_exists

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

    # Handle private chat scenario (existing flow)
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

    if is_new_user:
        # Welcome message for new users
        greeting = f"Hello {db_user.get('full_name')}! Welcome to GullyGuru. "
        if from_group:
            greeting = f"Hello {db_user.get('full_name')}! Welcome to GullyGuru. "

        await update.message.reply_text(
            f"{greeting}"
            "You are now registered as a player! 🎉\n\n"
            "You can now participate in cricket fantasy gaming with GullyGuru."
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
                "Ready to build your team?", reply_markup=reply_markup
            )

            # If this was initiated from a group, send a confirmation to the group
            if from_group:
                try:
                    await context.bot.send_message(
                        from_group,
                        f"🎉 @{user.username or db_user.get('full_name')} has successfully registered with GullyGuru!\n"
                        "They're now setting up their initial squad.",
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send confirmation to group {from_group}: {e}"
                    )
    else:
        # Existing user
        welcome_message = (
            f"Welcome back, {db_user.get('full_name')}! What would you like to do?\n\n"
        )

        # Add group context if applicable
        if from_group:
            welcome_message = (
                f"Welcome back, {db_user.get('full_name')}! "
                f"I see you're joining us from a group chat.\n\n"
            )

        welcome_message += "Use /help to see available commands."
        await update.message.reply_text(welcome_message)

    # Store the chat_id in user_data for context
    context.user_data["from_group"] = from_group
    return ConversationHandler.END


async def handle_group_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /start command when used in a group chat.

    Two modes:
    1. When used without mentioning a specific user: Checks all members and prompts unregistered users
    2. When a user initiates it themselves: Sends a welcome message and directs them to private chat
    """
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Check if this is a user initiating their own registration
    if update.message.from_user.id == user.id:
        # User is starting their own registration from the group
        deep_link = f"https://t.me/{context.bot.username}?start=from_group_{chat_id}"

        # Ensure user exists in database
        db_user = await ensure_user_exists(user)
        if not db_user:
            # User creation failed
            logger.error(f"Failed to create user {user.id} in database")
            await update.message.reply_text(
                "Sorry, there was an error registering you. Please try again later."
            )
            return ConversationHandler.END

        # Check if this is a new user (just created) or an existing user
        is_new_user = db_user.get("created_at") == db_user.get("updated_at")

        if is_new_user:
            # Send a welcome message in the group
            await update.message.reply_text(
                f"👋 Welcome to GullyGuru, {db_user.get('full_name')}!\n\n"
                "You are now registered as a player! 🎉\n\n"
                "I've sent you a private message to continue setting up your squad.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Open Private Chat", url=deep_link)]]
                ),
            )

            # Try to send a private message to the user
            try:
                # Check if user has a squad and prompt accordingly
                squad = await api_client.get_user_squad_submission(user.id)
                if not squad:
                    await context.bot.send_message(
                        user.id,
                        f"Hello {db_user.get('full_name')}! 👋\n\n"
                        "Welcome to GullyGuru, the cricket fantasy gaming platform!\n\n"
                        "You're now registered and ready to start playing.\n\n"
                        "📋 *Next Step: Submit Your Initial Squad*\n\n"
                        "To participate in the game, you need to select your initial team of 18 players (Round 0).\n\n"
                        "Use the /submit\\_squad command to start building your team.",
                        parse_mode="MarkdownV2",
                    )
            except Exception as e:
                logger.error(f"Failed to send private message to user {user.id}: {e}")
                # Inform the user they need to start a private chat
                await update.message.reply_text(
                    "I couldn't send you a private message. Please start a private chat with me first.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Start Private Chat", url=deep_link)]]
                    ),
                )
        else:
            # Existing user
            await update.message.reply_text(
                f"Welcome back, {db_user.get('full_name')}! You're already registered.\n\n"
                "You can continue in private chat for more options.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Open Private Chat", url=deep_link)]]
                ),
            )

        # Get the gully for this group
        gully = await api_client.get_gully_by_chat_id(chat_id)
        if gully:
            # Add user to this gully if not already a member
            from src.bot.utils.user_management import ensure_user_in_gully

            await ensure_user_in_gully(user.id, gully["id"])

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
            "/start - Register and start using the bot\n"
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
    Handle the /check_members command.
    This command allows admins to manually trigger a check of all group members
    and prompt unregistered users to start the bot.
    """
    # Only allow in group chats
    chat_type = update.effective_chat.type
    if chat_type not in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in group chats.")
        return

    # Check if the user is an admin
    user = update.effective_user
    try:
        chat_member = await context.bot.get_chat_member(
            update.effective_chat.id, user.id
        )
        if chat_member.status not in ["administrator", "creator"]:
            await update.message.reply_text(
                "This command can only be used by group administrators."
            )
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        await update.message.reply_text(
            "I couldn't verify your admin status. Please try again later."
        )
        return

    # Trigger the group member check
    await handle_group_start(update, context)


async def handle_start_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callbacks from the start command flow."""
    query = update.callback_query
    await query.answer()

    if query.data == "start_submit_squad":
        # Redirect to submit_squad command
        await query.message.reply_text(
            "Let's build your team! Starting the squad submission process...\n\n"
            "You'll need to select 18 players for your initial squad."
        )
        # Import here to avoid circular imports
        from src.bot.handlers.auction import submit_squad_command

        await submit_squad_command(update, context)
    elif query.data == "start_use_telegram_name":
        # Use the user's Telegram name for registration
        user = update.effective_user
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"

        # Register user with their Telegram name
        try:
            await api_client.register_user(user.id, name, user.username)

            # Confirmation message with personalized greeting
            await query.message.reply_text(
                f"Thank you, {name}! You are now registered as a player. 🎉\n\n"
                f"You can now participate in cricket fantasy gaming with GullyGuru!"
            )

            # Check if user has a squad and prompt accordingly
            squad = await api_client.get_user_squad_submission(user.id)
            if not squad:
                # Prompt user to submit squad with clear instructions
                await query.message.reply_text(
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
                await query.message.reply_text(
                    "Ready to build your team?", reply_markup=reply_markup
                )

                # If this was initiated from a group, send a confirmation to the group
                if "from_group" in context.user_data:
                    group_id = context.user_data["from_group"]
                    try:
                        await context.bot.send_message(
                            group_id,
                            f"🎉 @{user.username or name} has successfully registered with GullyGuru!\n"
                            f"They're now setting up their initial squad.",
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to send confirmation to group {group_id}: {e}"
                        )
            else:
                # User already has a squad
                await query.message.reply_text(
                    "You've already submitted your initial squad. Great job! 👍\n\n"
                    "Use /myteam to view your current team or /help to see all available commands."
                )
        except Exception as e:
            logger.error(f"Error registering user with Telegram name: {e}")
            await query.message.reply_text(
                "Sorry, there was an error registering your account. Please try again later."
            )
    else:
        await query.message.reply_text(
            "Unknown option. Please use /help to see available commands."
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
