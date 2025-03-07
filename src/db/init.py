"""
Database initialization and migration utilities.
"""

import logging
import os
import subprocess
from pathlib import Path

from sqlmodel import SQLModel, create_engine

# Import all models to ensure they're registered with SQLModel.metadata
import src.db.models  # noqa: F401

# Set up logging
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_database_url():
    """Get the database URL from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return database_url


def create_db_engine():
    """Create and return a database engine."""
    database_url = get_database_url()
    return create_engine(database_url, echo=False)


async def run_migrations():
    """Run database migrations using Alembic."""
    try:
        logger.info("Running database migrations...")

        # Check if we're running in a development environment
        if os.getenv("ENVIRONMENT") == "development":
            # In development, use pipenv
            result = subprocess.run(
                ["pipenv", "run", "alembic", "upgrade", "head"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        else:
            # In production, use direct alembic command
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        if result.returncode == 0:
            logger.info("Migrations completed successfully")
        else:
            logger.error(f"Migration failed: {result.stderr}")

        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to run migrations: {str(e)}")
        return False


async def create_tables_if_not_exist():
    """Create tables using SQLModel if they don't exist (fallback)."""
    try:
        logger.info("Creating tables using SQLModel...")
        engine = create_db_engine()
        SQLModel.metadata.create_all(engine)
        logger.info("Tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        return False


async def init_db():
    """Initialize database and run migrations."""
    # First try to run migrations
    migration_success = await run_migrations()

    # If migrations fail, try to create tables directly
    if not migration_success:
        logger.warning("Migrations failed, attempting to create tables directly")
        await create_tables_if_not_exist()

    return True


# Function to be called during application startup
async def startup_db_init():
    """Initialize the database during application startup."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialization completed")
