import asyncio
import logging
from src.bot.bot import create_application


async def main():
    """Start the bot."""
    # Configure logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    # Create and start the application
    app = await create_application()

    # Log startup
    logger.info("Bot started successfully")

    # Keep the bot running
    await app.updater.start_polling()
    await app.updater.stop()


if __name__ == "__main__":
    asyncio.run(main())
