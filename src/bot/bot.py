"""
Main bot module for GullyGuru.
Handles bot initialization, command registration, and onboarding functionality.
"""

import os
import logging
import asyncio
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Import features module for handler registration
from src.bot.features import register_all_features
from src.bot.api_client.base import initialize_api_client
from src.bot.api_client.onboarding import get_onboarding_client

# Import settings
from src.utils.config import settings

# Import logging configuration
from src.utils.logging_config import configure_logging, log_exception

# Import decorators
from src.utils.decorators import log_function_call

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging with default settings
configure_logging(verbose=False)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Set higher log levels for noisy libraries to reduce output
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)


# Create a filter to exclude repetitive messages
class MessageFilter(logging.Filter):
    """Filter to exclude repetitive log messages."""

    def __init__(self):
        super().__init__()
        self.last_message = ""

    def filter(self, record):
        # Skip getUpdates messages completely
        if "getUpdates" in record.getMessage():
            return False

        # Skip repetitive HTTP Request messages
        if "HTTP Request: " in record.getMessage():
            # Only show if it's not a polling request
            return "getUpdates" not in record.getMessage()

        # Allow all other messages
        return True


# Apply the filter to the root logger
root_logger = logging.getLogger()
root_logger.addFilter(MessageFilter())


# Main Menu functionality
@log_function_call
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the main menu to the user.
    This is the central navigation point for the bot in private chats.
    """
    user = update.effective_user

    try:
        # Get API client
        client = await get_onboarding_client()

        # Get user from database
        db_user = await client.get_user(user.id)
        if not db_user:
            # Create user if not exists
            db_user = await client.create_user(
                telegram_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )

        if not db_user:
            if update.callback_query:
                await update.callback_query.answer("Error accessing your account")
                await update.callback_query.edit_message_text(
                    "❌ Sorry, there was an error with your account. Please try again later."
                )
            else:
                await update.message.reply_text(
                    "❌ Sorry, there was an error with your account. Please try again later."
                )
            return

        # Get user's active gully
        active_gully = None
        active_gully_id = context.user_data.get("active_gully_id")

        if active_gully_id:
            # If we have an active gully ID in context, use it
            active_gully = await client.get_gully(active_gully_id)
            logger.debug(f"Active gully from context: {active_gully}")

        # Get all gullies the user is part of
        user_gullies = await client.get_user_gullies(user_id=db_user["id"])
        logger.debug(f"User gullies: {user_gullies}")

        gully_count = len(user_gullies) if user_gullies else 0

        # If user has no active gully or is part of multiple gullies and this is not a callback from gully selection,
        # show gully selection first
        if (not active_gully or gully_count > 1) and not context.user_data.get(
            "from_gully_selection"
        ):
            # Reset the flag for future calls
            if context.user_data.get("from_gully_selection"):
                context.user_data["from_gully_selection"] = False

            # If user has no gullies, show message
            if gully_count == 0:
                if update.callback_query:
                    await update.callback_query.edit_message_text(
                        "You are not part of any gully. Please join a gully first by clicking the link in a group chat."
                    )
                else:
                    await update.message.reply_text(
                        "You are not part of any gully. Please join a gully first by clicking the link in a group chat."
                    )
                return

            # Show gully selection
            await show_gully_selection(update, context)
            return

        # Check if user is an admin of any gully
        is_admin = False
        for gully_data in user_gullies:
            # Check different possible structures
            if "role" in gully_data and gully_data["role"] == "admin":
                is_admin = True
                break
            elif (
                "gully" in gully_data
                and "role" in gully_data
                and gully_data["role"] == "admin"
            ):
                is_admin = True
                break

        # Create main menu keyboard with feature-prefixed callbacks
        keyboard = [
            [
                InlineKeyboardButton("My Squad", callback_data="squad_view"),
                InlineKeyboardButton("Squad Menu", callback_data="squad_menu"),
            ],
            [InlineKeyboardButton("Auctions", callback_data="auction_view")],
            [InlineKeyboardButton("Transfers", callback_data="transfer_view")],
            [InlineKeyboardButton("Leaderboard", callback_data="leaderboard_view")],
            [InlineKeyboardButton("Help", callback_data="help_view")],
        ]

        # Add Switch Gully button if user is part of multiple gullies
        if gully_count > 1:
            keyboard.append(
                [InlineKeyboardButton("Switch Gully", callback_data="gully_switch")]
            )

        # Add Admin Panel button if user is an admin
        if is_admin:
            keyboard.append(
                [InlineKeyboardButton("Admin Panel", callback_data="admin_view")]
            )

        # Add Cancel button
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="menu_cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Create message text with active gully information
        if active_gully:
            message_text = (
                f"🏏 *GullyGuru Main Menu* 🏏\n\n"
                f"Active Gully: *{active_gully.get('name', 'Unknown')}*\n\n"
                "Please select an option:"
            )
        else:
            message_text = (
                "🏏 *GullyGuru Main Menu* 🏏\n\n"
                "You don't have an active gully. Please join a gully first.\n\n"
                "Please select an option:"
            )

        # Send or edit message based on update type
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Error in show_main_menu: {e}", exc_info=True)
        message = "❌ Sorry, there was an error showing the main menu. Please try again later."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)


@log_function_call
async def show_gully_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Show a list of gullies the user is part of for selection.
    """
    user = update.effective_user
    logger.info(f"Showing gully selection for user {user.id}")

    # Get API client
    client = await get_onboarding_client()

    # Get user from database
    db_user = await client.get_user(user.id)
    if not db_user:
        logger.error(f"User {user.id} not found in database")
        message = "❌ Error accessing your account. Please try again later."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Get user's active gully
    active_gully_id = context.user_data.get("active_gully_id")
    logger.info(f"Active gully ID: {active_gully_id}")

    # Get all gullies the user is part of
    try:
        user_gullies = await client.get_user_gullies(user_id=db_user["id"])
        logger.info(
            f"Found {len(user_gullies) if user_gullies else 0} gullies for user {user.id}"
        )

        # Debug log to see the structure
        logger.debug(f"User gullies response: {user_gullies}")

        if not user_gullies or len(user_gullies) == 0:
            logger.warning(f"No gullies found for user {user.id}")
            message = "You are not part of any gully. Please join a gully first."
            if update.callback_query:
                await update.callback_query.edit_message_text(message)
            else:
                await update.message.reply_text(message)
            return

        # Create keyboard with gully options
        keyboard = []

        # Process each gully based on its structure
        for gully_data in user_gullies:
            # Debug log for each gully
            logger.debug(f"Processing gully data: {gully_data}")

            gully_id = None
            gully_name = None

            # Check if this is a direct gully object
            if "id" in gully_data and "name" in gully_data:
                gully_id = gully_data["id"]
                gully_name = gully_data["name"]
                logger.info(f"Found direct gully: {gully_name} (ID: {gully_id})")
            # Check if this is a participation with embedded gully
            elif "gully" in gully_data and "id" in gully_data["gully"]:
                gully_id = gully_data["gully"]["id"]
                gully_name = gully_data["gully"]["name"]
                logger.info(f"Found embedded gully: {gully_name} (ID: {gully_id})")
            # Check if this is a participation with gully_id
            elif "gully_id" in gully_data:
                gully_id = gully_data["gully_id"]
                # We need to fetch the gully name
                gully = await client.get_gully(gully_id)
                if gully:
                    gully_name = gully["name"]
                    logger.info(f"Found gully by ID: {gully_name} (ID: {gully_id})")
                else:
                    gully_name = f"Gully {gully_id}"
                    logger.warning(f"Could not fetch gully name for ID: {gully_id}")

            # Skip if we couldn't determine the gully ID or name
            if not gully_id or not gully_name:
                logger.warning(f"Skipping gully with unknown structure: {gully_data}")
                continue

            # Mark active gully with a star
            if active_gully_id and gully_id == active_gully_id:
                gully_name = f"★ {gully_name} (Active)"

            callback_data = f"select_gully_{gully_id}"
            logger.info(
                f"Adding button for gully: {gully_name} with callback: {callback_data}"
            )

            keyboard.append(
                [InlineKeyboardButton(gully_name, callback_data=callback_data)]
            )

        # Only add Back button if this is called from the main menu (not on startup)
        if update.callback_query and update.callback_query.data == "gully_switch":
            logger.info("Adding 'Back to Main Menu' button")
            keyboard.append(
                [InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]
            )

        logger.info(f"Created keyboard with {len(keyboard)} buttons")
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = "Please select a gully to continue:"

        if update.callback_query:
            logger.info("Editing message with gully selection keyboard")
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
            )
        else:
            logger.info("Sending new message with gully selection keyboard")
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
            )
    except Exception as e:
        # Log the error
        logger.error(f"Error in show_gully_selection: {e}", exc_info=True)
        message = "❌ Sorry, there was an error retrieving your gullies. Please try again later."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)


@log_function_call
async def handle_gully_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle gully selection callback.
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    callback_data = query.data

    # Extract gully ID from callback data
    try:
        gully_id = int(callback_data.replace("select_gully_", ""))
    except ValueError:
        logger.error(f"Invalid gully ID in callback data: {callback_data}")
        await query.edit_message_text("❌ Invalid gully selection. Please try again.")
        return

    # Get API client
    client = await get_onboarding_client()

    # Get user from database
    db_user = await client.get_user(user.id)
    if not db_user:
        await query.edit_message_text(
            "❌ Error accessing your account. Please try again later."
        )
        return

    try:
        # Get the gully
        gully = await client.get_gully(gully_id)
        if not gully:
            logger.error(f"Gully with ID {gully_id} not found")
            await query.edit_message_text(
                "❌ The selected gully was not found. Please try again."
            )
            return

        # Store in context for future use
        context.user_data["active_gully_id"] = gully_id
        context.user_data["from_gully_selection"] = True

        # Get the gully name for the message
        gully_name = gully.get("name", f"Gully {gully_id}")

        # Show a confirmation message
        await query.edit_message_text(
            f"✅ Active gully set to *{gully_name}*.",
            parse_mode="Markdown",
        )

        # Show main menu for the selected gully
        await show_main_menu(update, context)
    except Exception as e:
        logger.error(f"Error in handle_gully_selection: {e}", exc_info=True)
        await query.edit_message_text(
            "❌ An error occurred while selecting the gully. Please try again later."
        )


async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the help menu with basic instructions.
    """
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    help_text = (
        "📋 *GullyGuru Help* 📋\n\n"
        "Need assistance? Here's how to use GullyGuru:\n\n"
        "• You can see your squad with [My Squad]\n"
        "• To buy players, use [Auctions] or [Transfers]\n"
        "• Check your ranking in [Leaderboard]\n"
        "• For admin tasks, see [Admin Panel]\n\n"
        "For more help, contact @GullyGuruSupport"
    )

    await update.callback_query.edit_message_text(
        help_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def start_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle /start command to show the main menu.
    This replaces the original start_command in onboarding.py for simplicity.
    """
    chat = update.effective_chat

    # Only allow in private chats
    if chat.type != "private":
        return

    # Check if user came from deep link
    args = context.args
    telegram_group_id = None

    if args and args[0].startswith("group_"):
        try:
            telegram_group_id = int(args[0].split("_")[1])
            logger.info(
                f"User {update.effective_user.id} started registration from group {telegram_group_id}"
            )
            context.user_data["telegram_group_id"] = telegram_group_id
        except (ValueError, IndexError):
            logger.warning(f"Invalid deep link parameter: {args[0]}")

    # Show the main menu
    await show_main_menu(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the dispatcher."""
    # Log the error with full traceback
    logger.error("Exception while handling an update", exc_info=context.error)

    # Get the exception info
    error = context.error

    # Log detailed information about the update that caused the error
    if update:
        if hasattr(update, "effective_message") and update.effective_message:
            logger.error(f"Message that caused error: {update.effective_message.text}")
        if hasattr(update, "callback_query") and update.callback_query:
            logger.error(
                f"Callback query that caused error: {update.callback_query.data}"
            )
        if hasattr(update, "effective_user") and update.effective_user:
            logger.error(
                f"User that triggered error: {update.effective_user.id} ({update.effective_user.username or update.effective_user.first_name})"
            )

    # Notify user about the error if possible
    try:
        if hasattr(update, "effective_message") and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, something went wrong. The error has been logged and will be addressed."
            )
        elif hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.answer(
                "Sorry, something went wrong. Please try again."
            )
    except Exception as e:
        logger.error(f"Error while sending error message to user: {e}")


async def wait_for_api(max_retries=30, retry_interval=2):
    """
    Wait for the API to be available.

    Args:
        max_retries: Maximum number of retries
        retry_interval: Interval between retries in seconds

    Returns:
        bool: True if API is available, False otherwise
    """
    api_base_url = settings.API_BASE_URL
    health_url = f"{api_base_url}/health"

    logger.info(f"Checking API availability at {health_url}")

    retries = 0
    while retries < max_retries:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                logger.debug(f"Attempt {retries+1}/{max_retries} to connect to API")
                response = await client.get(health_url)

                if response.status_code == 200:
                    # Check if database is also healthy
                    try:
                        data = response.json()
                        db_status = data.get("database", "unknown")

                        if db_status == "healthy":
                            logger.info("API and database are available and healthy!")
                            return True
                        else:
                            logger.warning(
                                f"API is available but database status is: {db_status}"
                            )
                    except Exception as e:
                        logger.warning(
                            f"API returned status 200 but response is not valid JSON: {str(e)}"
                        )
                else:
                    logger.warning(
                        f"API returned status code {response.status_code}, retrying..."
                    )
        except httpx.ConnectError:
            logger.warning("Connection to API failed, retrying...")
        except httpx.ReadTimeout:
            logger.warning("API request timed out, retrying...")
        except Exception as e:
            logger.warning(f"API check failed with error: {str(e)}")

        retries += 1
        if retries < max_retries:
            logger.info(
                f"Retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})"
            )
            await asyncio.sleep(retry_interval)

    logger.error(f"API not available after {max_retries} attempts")
    return False


async def set_log_level_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Command handler to set the logging level.
    Usage: /loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
    """
    # Check if the user is authorized (only allow the first user who uses this command)
    if "admin_id" not in context.bot_data:
        context.bot_data["admin_id"] = update.effective_user.id
        logger.info(
            f"Setting {update.effective_user.id} as admin for log level commands"
        )

    if update.effective_user.id != context.bot_data.get("admin_id"):
        await update.message.reply_text("You are not authorized to change log levels.")
        return

    # Get the requested log level
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "Please specify a log level: /loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]"
        )
        return

    level_name = context.args[0].upper()

    # Map string to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    if level_name not in level_map:
        await update.message.reply_text(
            f"Invalid log level: {level_name}. "
            f"Please use one of: {', '.join(level_map.keys())}"
        )
        return

    # Set the log level
    logging.getLogger().setLevel(level_map[level_name])

    # Confirm the change
    await update.message.reply_text(f"Log level set to {level_name}")


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Command handler to dump debug information.
    Usage: /debug
    """
    # Check if the user is authorized (only allow the first user who uses this command)
    if "admin_id" not in context.bot_data:
        context.bot_data["admin_id"] = update.effective_user.id
        logger.info(f"Setting {update.effective_user.id} as admin for debug commands")

    if update.effective_user.id != context.bot_data.get("admin_id"):
        await update.message.reply_text("You are not authorized to use debug commands.")
        return

    # Collect debug information
    debug_info = []

    # User data
    debug_info.append("User Data:")
    for key, value in context.user_data.items():
        debug_info.append(f"  {key}: {value}")

    # Chat data
    debug_info.append("\nChat Data:")
    for key, value in context.chat_data.items():
        debug_info.append(f"  {key}: {value}")

    # Bot data
    debug_info.append("\nBot Data:")
    for key, value in context.bot_data.items():
        debug_info.append(f"  {key}: {value}")

    # Update information
    debug_info.append("\nUpdate Information:")
    debug_info.append(f"  Update ID: {update.update_id}")
    debug_info.append(f"  Chat ID: {update.effective_chat.id}")
    debug_info.append(f"  User ID: {update.effective_user.id}")

    # Send the debug information
    debug_text = "\n".join(debug_info)
    await update.message.reply_text(debug_text)


async def debug_participant_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Command handler to debug participant data.
    Usage: /debug_participant
    """
    user = update.effective_user

    # Get user data
    try:
        onboarding_client = await get_onboarding_client()
        user_data = await onboarding_client.get_user(user.id)

        if not user_data:
            await update.message.reply_text(
                "You are not registered. Please use /start to register."
            )
            return

        user_id = user_data["id"]

        # Get active gully
        active_gully_id = context.user_data.get("active_gully_id")
        if not active_gully_id:
            await update.message.reply_text(
                "No active gully set. Please use /gully to select a gully."
            )
            return

        # Try to get participant data
        debug_info = [
            f"User ID: {user_id}",
            f"Telegram ID: {user.id}",
            f"Active Gully ID: {active_gully_id}",
        ]

        # Try onboarding client
        try:
            participant1 = await onboarding_client.get_participant(
                user_id, active_gully_id
            )
            debug_info.append("\nParticipant data from onboarding client:")
            if participant1:
                debug_info.append(f"Participant ID: {participant1.get('id')}")
                debug_info.append(f"Team Name: {participant1.get('team_name')}")
            else:
                debug_info.append("No participant data found")
        except Exception as e1:
            debug_info.append(
                f"Error getting participant from onboarding client: {str(e1)}"
            )

        # Send debug info
        await update.message.reply_text("\n".join(debug_info))

    except Exception as e:
        logger.error(f"Error in debug_participant: {str(e)}", exc_info=True)
        await update.message.reply_text(f"Error: {str(e)}")


@log_function_call
async def handle_main_menu_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle callbacks from the main menu.
    Routes to appropriate sub-menus based on user selection.
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    logger.info(f"Main menu callback received: {callback_data}")

    # For squad-related callbacks, ensure participant_id is set
    if callback_data == "squad_view" or callback_data.startswith("squad_"):
        if not await ensure_participant_id(update, context):
            return

    # Simply delegate to the appropriate feature based on the callback prefix
    if callback_data == "squad_view":
        # This specific callback should be handled by the squad handler
        # Import the necessary function to avoid circular imports
        from src.bot.features.squad import view_squad

        logger.info("Directly handling squad_view callback")
        return await view_squad(update, context)
    elif callback_data.startswith("squad_"):
        # Log that we're delegating to squad handlers
        logger.info(f"Delegating '{callback_data}' to squad handlers")
        # Let the squad handlers handle this
        return
    elif callback_data.startswith("auction_"):
        # Placeholder for auction feature (not implemented yet)
        logger.info("Showing auction placeholder")
        await query.edit_message_text(
            "🏏 *Auctions* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to participate in player auctions here.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
            ),
        )
        return
    elif callback_data.startswith("transfer_"):
        # Placeholder for transfer feature (not implemented yet)
        logger.info("Showing transfer placeholder")
        await query.edit_message_text(
            "🏏 *Transfers* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to transfer players here.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
            ),
        )
        return
    elif callback_data.startswith("leaderboard_"):
        # Placeholder for leaderboard feature (not implemented yet)
        logger.info("Showing leaderboard placeholder")
        await query.edit_message_text(
            "🏏 *Leaderboard* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to view the leaderboard here.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
            ),
        )
        return
    elif callback_data == "help_view":
        logger.info("Showing help menu")
        await show_help_menu(update, context)
    elif callback_data == "menu_cancel":
        logger.info("Returning to main menu")
        await query.edit_message_text("Operation cancelled.")
        await show_main_menu(update, context)
    elif callback_data == "gully_switch":
        logger.info("Showing gully selection")
        await show_gully_selection(update, context)
    else:
        logger.warning(f"Unknown callback data: {callback_data}")
        await query.edit_message_text(
            "❌ Unknown option selected. Please try again.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]]
            ),
        )


@log_function_call
async def handle_squad_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle squad-related callbacks.
    This is a router function that delegates to specific squad feature handlers.
    """
    query = update.callback_query
    await query.answer()

    # Ensure participant_id is set
    if not await ensure_participant_id(update, context):
        return

    callback_data = query.data
    logger.info(f"Squad callback received: {callback_data}")

    # Import squad feature functions here to avoid circular imports
    from src.bot.features.squad import (
        show_all_players,
        view_squad,
        show_squad_menu,
        SQUAD_MENU,
        PLAYER_FILTER,
        PLAYER_SELECTION,
        REMOVE_PLAYER,
        CONFIRM_SUBMISSION,
        MULTI_SELECT,
        MULTI_REMOVE,
    )

    # Delegate to the appropriate squad handler based on the callback data
    if callback_data == SQUAD_MENU.START_BUILDING:
        logger.info("Delegating to show_all_players")
        # This should show the player selection screen
        return await show_all_players(update, context)
    elif callback_data == SQUAD_MENU.VIEW_SQUAD:
        logger.info("Delegating to view_squad")
        # This should show the current squad
        return await view_squad(update, context)
    elif callback_data == SQUAD_MENU.SUBMIT_SQUAD:
        logger.info("Delegating to confirm_submission")
        # This should show the submission confirmation
        from src.bot.features.squad import confirm_submission

        return await confirm_submission(update, context)
    elif callback_data == SQUAD_MENU.BACK_TO_MENU:
        logger.info("Delegating to show_squad_menu")
        # This should show the squad menu
        return await show_squad_menu(update, context)
    elif (
        callback_data.startswith(PLAYER_FILTER.BATSMEN)
        or callback_data.startswith(PLAYER_FILTER.BOWLERS)
        or callback_data.startswith(PLAYER_FILTER.ALL_ROUNDERS)
        or callback_data.startswith(PLAYER_FILTER.WICKET_KEEPERS)
        or callback_data.startswith(PLAYER_FILTER.ALL_PLAYERS)
        or callback_data.startswith(PLAYER_FILTER.SEARCH_BY_NAME)
    ):
        logger.info("Delegating to show_all_players for filter")
        # This should filter players
        return await show_all_players(update, context)
    elif (
        callback_data.startswith(PLAYER_SELECTION.SELECT_PLAYER)
        or callback_data.startswith(PLAYER_SELECTION.PAGE_PREFIX)
        or callback_data == PLAYER_SELECTION.MORE_PLAYERS
    ):
        logger.info("Delegating to show_all_players for player selection")
        # This should handle player selection
        return await show_all_players(update, context)
    elif (
        callback_data.startswith(MULTI_SELECT.TOGGLE_SELECT)
        or callback_data == MULTI_SELECT.CONFIRM_MULTI_SELECT
        or callback_data == MULTI_SELECT.CANCEL_MULTI_SELECT
    ):
        logger.info("Delegating to handle_multi_select_callback")
        # This should handle multi-select
        from src.bot.features.squad import handle_multi_select_callback

        return await handle_multi_select_callback(update, context)
    elif (
        callback_data.startswith(REMOVE_PLAYER.REMOVE_PLAYER)
        or callback_data == REMOVE_PLAYER.MULTI_REMOVE
    ):
        logger.info("Delegating to handle_view_squad_callback")
        # This should handle player removal
        from src.bot.features.squad import handle_view_squad_callback

        return await handle_view_squad_callback(update, context)
    elif (
        callback_data.startswith(MULTI_REMOVE.TOGGLE_REMOVE)
        or callback_data == MULTI_REMOVE.CONFIRM_MULTI_REMOVE
        or callback_data == MULTI_REMOVE.CANCEL_MULTI_REMOVE
    ):
        logger.info("Delegating to handle_multi_remove_callback")
        # This should handle multi-remove
        from src.bot.features.squad import handle_multi_remove_callback

        return await handle_multi_remove_callback(update, context)
    elif (
        callback_data == CONFIRM_SUBMISSION.CONFIRM
        or callback_data == CONFIRM_SUBMISSION.CANCEL
    ):
        logger.info("Delegating to handle_submission_confirmation")
        # This should handle submission confirmation
        from src.bot.features.squad import handle_submission_confirmation

        return await handle_submission_confirmation(update, context)
    else:
        logger.warning(f"Unknown squad callback: {callback_data}")
        # Fallback to show squad menu
        return await show_squad_menu(update, context)


@log_function_call
async def ensure_participant_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """
    Ensure that participant_id is set in the context.
    If not, try to fetch it and set it.

    Returns:
        bool: True if participant_id is set, False otherwise
    """
    if context.user_data.get("participant_id"):
        return True

    user = update.effective_user
    active_gully_id = context.user_data.get("active_gully_id")

    if not active_gully_id:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "No active gully selected. Please select a gully first.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Back to Main Menu", callback_data="main_menu"
                            )
                        ]
                    ]
                ),
            )
        else:
            await update.message.reply_text(
                "No active gully selected. Please select a gully first.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Back to Main Menu", callback_data="main_menu"
                            )
                        ]
                    ]
                ),
            )
        return False

    try:
        # Get user data
        onboarding_client = await get_onboarding_client()
        user_data = await onboarding_client.get_user_by_telegram_id(user.id)

        if not user_data or "id" not in user_data:
            logger.error(f"Could not find user with telegram_id {user.id}")
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "Error retrieving your user data. Please try again later.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Back to Main Menu", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                )
            else:
                await update.message.reply_text(
                    "Error retrieving your user data. Please try again later.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Back to Main Menu", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                )
            return False

        user_id = user_data["id"]
        context.user_data["user_id"] = user_id

        # Get participant data
        participant_data = await onboarding_client.get_participant_by_user_id(
            user_id, active_gully_id
        )

        if not participant_data or "id" not in participant_data:
            logger.error(
                f"Could not find participant for user {user_id} in gully {active_gully_id}"
            )
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "You are not registered as a participant in this gully. Please join the gully first.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Back to Main Menu", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                )
            else:
                await update.message.reply_text(
                    "You are not registered as a participant in this gully. Please join the gully first.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Back to Main Menu", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                )
            return False

        participant_id = participant_data["id"]
        context.user_data["participant_id"] = participant_id
        logger.info(f"Set participant_id to {participant_id} for user {user.id}")
        return True

    except Exception as e:
        logger.error(f"Error ensuring participant_id: {str(e)}", exc_info=True)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "An error occurred while retrieving your participant data. Please try again later.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Back to Main Menu", callback_data="main_menu"
                            )
                        ]
                    ]
                ),
            )
        else:
            await update.message.reply_text(
                "An error occurred while retrieving your participant data. Please try again later.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Back to Main Menu", callback_data="main_menu"
                            )
                        ]
                    ]
                ),
            )
        return False


async def main_async():
    """Initialize and start the bot."""
    try:
        # Check if API is running and wait until it's available
        logger.info("Starting GullyGuru bot...")
        logger.info("Checking if API is running...")
        api_available = await wait_for_api(
            max_retries=60, retry_interval=5
        )  # Wait up to 5 minutes

        if not api_available:
            logger.error("API is not available after maximum retries. Exiting...")
            return

        logger.info("API is available. Initializing bot...")

        # Initialize API client
        await initialize_api_client()
        logger.info("API client initialized successfully")

        # Create application
        application = Application.builder().token(BOT_TOKEN).build()

        # Register all feature handlers
        register_all_features(application)

        # Override the /start command with our simplified version
        application.add_handler(CommandHandler("start", start_command_handler))

        # Register debug and log level commands
        application.add_handler(CommandHandler("loglevel", set_log_level_command))
        application.add_handler(CommandHandler("debug", debug_command))
        application.add_handler(
            CommandHandler("debug_participant", debug_participant_command)
        )

        # Register gully selection handlers FIRST (more specific)
        application.add_handler(
            CallbackQueryHandler(handle_gully_selection, pattern="^select_gully_")
        )
        application.add_handler(
            CallbackQueryHandler(show_gully_selection, pattern="^gully_switch$")
        )

        # Register main menu and help handlers
        application.add_handler(
            CallbackQueryHandler(show_main_menu, pattern="^main_menu$")
        )
        application.add_handler(
            CallbackQueryHandler(show_help_menu, pattern="^help_view$")
        )

        # Add a direct handler for squad_view
        from src.bot.features.squad import view_squad

        application.add_handler(
            CallbackQueryHandler(view_squad, pattern="^squad_view$")
        )

        # Register squad-specific handlers with a more comprehensive pattern
        application.add_handler(
            CallbackQueryHandler(
                handle_squad_callback,
                pattern="^(start_building_squad|add_players|view_squad|submit_squad|back_to_menu|"
                "batsmen|bowlers|all_rounders|wicket_keepers|all_players|search_by_name|"
                "select_player|page_|more_players|toggle_select|confirm_multi_select|cancel_multi_select|"
                "remove_player|multi_remove|toggle_remove|confirm_multi_remove|cancel_multi_remove|"
                "confirm_final|cancel_submission).*$",
            )
        )

        # Register the main menu callback handler LAST, with a more specific pattern
        # that doesn't overlap with other handlers
        application.add_handler(
            CallbackQueryHandler(
                handle_main_menu_callback,
                pattern="^(squad_(?!view$)|auction_|transfer_|leaderboard_|menu_cancel).*$",
            )
        )

        # Register error handler
        application.add_error_handler(error_handler)

        # Initialize the application
        await application.initialize()

        # Start the bot
        logger.info("Starting the bot...")
        await application.start()
        await application.updater.start_polling()

        logger.info("Bot started successfully")

        # Keep the bot running until interrupted
        stop_signal = asyncio.Future()
        await stop_signal

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise


def main():
    """Run the bot."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
