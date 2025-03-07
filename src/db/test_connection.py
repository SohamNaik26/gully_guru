import asyncio
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from src.db.session import async_session

logger = logging.getLogger(__name__)


async def test_connection():
    """Test if the database connection is successful."""
    try:
        async with async_session() as session:
            # Test connection by executing a simple query
            await session.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(test_connection())
