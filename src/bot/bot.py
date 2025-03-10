#!/usr/bin/env python
"""
Main bot module for GullyGuru.
Handles bot initialization, command registration, and command scopes.
"""

import os
import logging
import asyncio
import httpx
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    ContextTypes,
)

# Import features module for handler registration
from src.bot.features import register_handlers
from src.bot.command_scopes import refresh_command_scopes
from src.bot.sync_manager import sync_all_groups

# Import settings
from src.utils.config import settings

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the dispatcher."""
    logger.error(f"Exception while handling an update: {context.error}")


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

        # Create application
        application = Application.builder().token(BOT_TOKEN).build()

        # Register all feature handlers
        register_handlers(application)

        # Register error handler
        application.add_error_handler(error_handler)

        # Initialize the application
        await application.initialize()

        # Set up command scopes
        await refresh_command_scopes(application)

        # Sync all groups and users using the improved sync manager
        logger.info("Starting comprehensive group and user synchronization...")
        try:
            sync_results = await sync_all_groups(application.bot)
            logger.info("Sync completed with the following results:")
            logger.info(f"- Groups processed: {sync_results.get('processed', 0)}")
            logger.info(f"- Gullies created: {sync_results.get('gullies_created', 0)}")
            logger.info(f"- Users added: {sync_results.get('users_added', 0)}")
            logger.info(f"- Errors encountered: {sync_results.get('errors', 0)}")

            # Schedule periodic sync every 6 hours
            async def periodic_sync():
                while True:
                    await asyncio.sleep(6 * 60 * 60)  # 6 hours
                    logger.info("Running scheduled group synchronization...")
                    try:
                        sync_results = await sync_all_groups(application.bot)
                        logger.info(
                            f"Scheduled sync completed: {sync_results['processed']} groups processed, "
                            f"{sync_results['users_added']} users added"
                        )
                    except Exception as e:
                        logger.error(f"Error in scheduled sync: {e}")

            # Start the periodic sync task
            asyncio.create_task(periodic_sync())
            logger.info("Scheduled periodic sync every 6 hours")

        except Exception as e:
            logger.error(f"Error during initial group synchronization: {e}")
            logger.info("Continuing with bot startup despite sync errors")

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
