"""
GullyGuru Bot - Fantasy Cricket Manager
Main bot file that initializes the bot and registers all handlers.
"""

import asyncio
import logging
import os
from functools import wraps
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
)

# Import command scopes
from src.bot.command_scopes import setup_command_scopes

# Import centralized client initialization
from src.bot.api_client.init import wait_for_api

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


class MessageFilter(logging.Filter):
    """Filter to exclude getUpdates messages from logs."""

    def __init__(self):
        super().__init__()
        self.last_update_id = 0

    def filter(self, record):
        # Skip getUpdates messages completely
        if "getUpdates" in record.getMessage():
            return False
        return True


# Add filter to logger
logging.getLogger("httpx").addFilter(MessageFilter())


def log_function_call(func):
    """Decorator to log function calls."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        update = next((arg for arg in args if isinstance(arg, Update)), None)
        user_id = (
            update.effective_user.id if update and update.effective_user else "Unknown"
        )
        logger.info(f"Function {func.__name__} called by user {user_id}")
        return await func(*args, **kwargs)

    return wrapper


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the dispatcher."""
    logger.error(f"Exception while handling an update: {context.error}")

    # Log the error to console
    import traceback

    traceback.print_exception(None, context.error, context.error.__traceback__)

    # Send a message to the user
    if update and isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred while processing your request. Please try again later."
        )


async def main_async():
    """Initialize and run the bot asynchronously."""
    # Check if token is available
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    # Wait for API to be available
    if not await wait_for_api():
        logger.error("API not available, exiting")
        return

    # Initialize the bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Set up command scopes
    await setup_command_scopes(application)

    # Register error handler
    application.add_error_handler(error_handler)

    # Register handlers
    logger.info("Registering handlers")

    # Register feature handlers
    setup_handlers(application)

    # Start the bot
    logger.info("Starting bot...")

    # Initialize and start the application
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    logger.info("Bot is running")

    # Keep the bot running until interrupted
    try:
        await asyncio.Event().wait()  # Run forever
    finally:
        # Properly shut down on exit
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def setup_handlers(application):
    """Set up all command handlers for the bot."""
    # Import feature modules
    from src.bot.features import (
        get_onboarding_handlers,
        get_squad_handlers,
        get_auction_handlers,
        get_player_release_handlers,
        get_auction_queue_handlers,
    )

    # Register auction callback handlers FIRST for higher priority
    logger.info("Registering auction queue handlers")
    auction_queue_handlers = get_auction_queue_handlers()
    for handler in auction_queue_handlers:
        if callable(handler):
            # Call the callback registration function first
            handler(application)

    # Then register regular handlers
    for handler in auction_queue_handlers:
        if not callable(handler):
            application.add_handler(handler)

    # Register onboarding handlers
    logger.info("Registering onboarding handlers")
    application.add_handlers(get_onboarding_handlers())

    logger.info("Registering player release handlers")
    application.add_handlers(get_player_release_handlers())

    logger.info("Registering auction handlers")
    application.add_handlers(get_auction_handlers())

    # Register squad handlers LAST to ensure lower priority
    logger.info("Registering squad handlers")
    application.add_handlers(get_squad_handlers())

    logger.info("All handlers registered successfully")


def main():
    """Run the bot."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
