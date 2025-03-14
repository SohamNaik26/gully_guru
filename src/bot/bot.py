#!/usr/bin/env python
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
)

# Import features module for handler registration
from src.bot.features import register_handlers
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
logging.getLogger("httpx").setLevel(
    logging.WARNING
)  # Only show warnings and errors for httpx
logging.getLogger("telegram").setLevel(
    logging.WARNING
)  # Only show warnings and errors for python-telegram-bot
logging.getLogger("telegram.ext").setLevel(
    logging.WARNING
)  # Only show warnings and errors for telegram extensions


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

        # Create main menu keyboard
        keyboard = [
            [InlineKeyboardButton("My Squad", callback_data="menu_my_squad")],
            [InlineKeyboardButton("Auctions", callback_data="menu_auctions")],
            [InlineKeyboardButton("Transfers", callback_data="menu_transfers")],
            [InlineKeyboardButton("Leaderboard", callback_data="menu_leaderboard")],
            [InlineKeyboardButton("Help", callback_data="menu_help")],
        ]

        # Add Switch Gully button if user is part of multiple gullies
        if gully_count > 1:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "Switch Gully", callback_data="menu_switch_gully"
                    )
                ]
            )

        # Add Admin Panel button if user is an admin
        if is_admin:
            keyboard.append(
                [InlineKeyboardButton("Admin Panel", callback_data="menu_admin")]
            )

        # Add Cancel button
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="menu_cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Create message text with active gully information
        if active_gully:
            message_text = (
                f"🏏 *GullyGuru Main Menu* 🏏\n\n"
                f"Active Gully: *{active_gully.get('name', 'Unknown')}*\n\n"
                f"Please select an option:"
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

    # Get API client
    client = await get_onboarding_client()

    # Get user from database
    db_user = await client.get_user(user.id)
    if not db_user:
        message = "❌ Error accessing your account. Please try again later."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Get user's active gully
    active_gully_id = context.user_data.get("active_gully_id")

    # Get all gullies the user is part of
    try:
        user_gullies = await client.get_user_gullies(user_id=db_user["id"])

        # Debug log to see the structure
        logger.debug(f"User gullies response: {user_gullies}")

        if not user_gullies or len(user_gullies) == 0:
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
            # Check if this is a participation with embedded gully
            elif "gully" in gully_data and "id" in gully_data["gully"]:
                gully_id = gully_data["gully"]["id"]
                gully_name = gully_data["gully"]["name"]
            # Check if this is a participation with gully_id
            elif "gully_id" in gully_data:
                gully_id = gully_data["gully_id"]
                # We need to fetch the gully name
                gully = await client.get_gully(gully_id)
                if gully:
                    gully_name = gully["name"]
                else:
                    gully_name = f"Gully {gully_id}"

            # Skip if we couldn't determine the gully ID or name
            if not gully_id or not gully_name:
                logger.warning(f"Skipping gully with unknown structure: {gully_data}")
                continue

            # Mark active gully with a star
            if active_gully_id and gully_id == active_gully_id:
                gully_name = f"★ {gully_name} (Active)"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        gully_name, callback_data=f"select_gully_{gully_id}"
                    )
                ]
            )

        # Only add Back button if this is called from the main menu (not on startup)
        if update.callback_query and update.callback_query.data == "menu_switch_gully":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "Back to Main Menu", callback_data="back_to_main_menu"
                    )
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = "Select a gully to continue:"

        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
            )
        else:
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

    if callback_data == "menu_my_squad":
        # Placeholder for My Squad feature
        await query.edit_message_text(
            "🏏 *My Squad* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to view and manage your squad here.",
            parse_mode="Markdown",
        )

    elif callback_data == "menu_auctions":
        # Placeholder for Auctions feature
        await query.edit_message_text(
            "🏏 *Auctions* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to participate in player auctions here.",
            parse_mode="Markdown",
        )

    elif callback_data == "menu_transfers":
        # Placeholder for Transfers feature
        await query.edit_message_text(
            "🏏 *Transfers* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to transfer players here.",
            parse_mode="Markdown",
        )

    elif callback_data == "menu_leaderboard":
        # Placeholder for Leaderboard feature
        await query.edit_message_text(
            "🏏 *Leaderboard* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to view the leaderboard here.",
            parse_mode="Markdown",
        )

    elif callback_data == "menu_help":
        await show_help_menu(update, context)

    elif callback_data == "menu_switch_gully":
        await show_gully_selection(update, context)

    elif callback_data == "menu_admin":
        # Placeholder for Admin Panel feature
        await query.edit_message_text(
            "🏏 *Admin Panel* 🏏\n\n"
            "This feature is coming soon!\n\n"
            "You'll be able to manage your gully here.",
            parse_mode="Markdown",
        )

    elif callback_data == "menu_cancel":
        await query.edit_message_text(
            "Operation cancelled. Type /start to show the menu again."
        )

    else:
        await query.edit_message_text(
            "Invalid option. Type /start to show the menu again."
        )


async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the help menu with basic instructions.
    """
    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data="back_to_main_menu")]
    ]
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


async def back_to_main_menu_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the 'Back to Main Menu' callback.
    Returns the user to the main menu from any sub-menu.
    """
    await show_main_menu(update, context)


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
    # Check if the user is authorized (you might want to restrict this to admins)
    if update.effective_user.id != YOUR_ADMIN_ID:  # Replace with your Telegram ID
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
    # Check if the user is authorized (you might want to restrict this to admins)
    if update.effective_user.id != YOUR_ADMIN_ID:  # Replace with your Telegram ID
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

        # Register onboarding handlers for group events
        register_handlers(application)

        # Override the /start command with our simplified version
        application.add_handler(CommandHandler("start", start_command_handler))

        # Register main menu handlers
        application.add_handler(
            CallbackQueryHandler(handle_main_menu_callback, pattern="^menu_")
        )
        application.add_handler(
            CallbackQueryHandler(
                back_to_main_menu_handler, pattern="^back_to_main_menu$"
            )
        )
        application.add_handler(
            CallbackQueryHandler(handle_gully_selection, pattern="^select_gully_")
        )

        # Register error handler
        application.add_error_handler(error_handler)

        # Register log level command
        application.add_handler(CommandHandler("loglevel", set_log_level_command))

        # Register debug command
        application.add_handler(CommandHandler("debug", debug_command))

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
