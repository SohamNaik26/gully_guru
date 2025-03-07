import os
from typing import Generator, AsyncGenerator
import logging

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
from src.utils.config import settings

load_dotenv()

logger = logging.getLogger(__name__)

# Log database connection details (with password masked)
db_url_masked = settings.DATABASE_URL.replace("://", "://***:***@", 1)
logger.info(f"Connecting to database: {db_url_masked}")

# Create engines
try:
    engine = create_engine(settings.DATABASE_URL, echo=settings.DATABASE_ECHO)
    
    # Use asyncpg for async operations
    async_engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.DATABASE_ECHO,
        # Add these options to handle timezone-aware datetime objects
        connect_args={"server_settings": {"timezone": "UTC"}},
    )
    logger.info("Database engines created successfully")
except Exception as e:
    logger.error(f"Failed to create database engines: {str(e)}")
    raise

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
async_session = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=async_engine
)


# Dependency for synchronous sessions
def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for synchronous operations.

    Yields:
        Session: SQLModel session
    """
    with Session(engine) as session:
        yield session


# Dependency for asynchronous sessions
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for asynchronous operations.

    Yields:
        AsyncSession: Async SQLModel session
    """
    async with async_session() as session:
        yield session


# Create all tables (for development only)
def create_db_and_tables():
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)


async def create_db_and_tables_async():
    """Create all tables in the database asynchronously."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Initialize database (for testing and development)
def init_db():
    """Initialize the database with tables and initial data."""
    create_db_and_tables()
    # Add initial data if needed


async def init_db_async():
    """Initialize the database asynchronously."""
    await create_db_and_tables_async()
    # Add initial data if needed
