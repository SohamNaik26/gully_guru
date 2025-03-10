from typing import Generator, AsyncGenerator
import logging
import asyncio
import os

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

from dotenv import load_dotenv
from src.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Log database connection
db_url_masked = settings.DATABASE_URL.replace("://", "://***:***@", 1)
logger.info(f"Connecting to database: {db_url_masked}")

# Connection pool settings
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # 30 minutes
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))  # 10 seconds
COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))  # 30 seconds

# Create engines
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=getattr(settings, "DB_ECHO", False),
    pool_pre_ping=True,
    pool_recycle=POOL_RECYCLE,
)

async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=getattr(settings, "DB_ECHO", False),
    future=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # Check connection validity before using it
    connect_args={
        "timeout": CONNECT_TIMEOUT,
        "command_timeout": COMMAND_TIMEOUT,
    },
)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds


# Dependency for synchronous sessions
def get_sync_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Dependency for asynchronous sessions with retry logic
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session with retry logic.

    Yields:
        AsyncSession: Database session
    """
    session = AsyncSessionLocal()
    retry_count = 0

    try:
        while retry_count < MAX_RETRIES:
            try:
                yield session
                break
            except Exception as e:
                retry_count += 1
                if "Operation timed out" in str(e) and retry_count < MAX_RETRIES:
                    logger.warning(
                        f"Database connection timed out, retrying ({retry_count}/{MAX_RETRIES})..."
                    )
                    await asyncio.sleep(
                        RETRY_DELAY * retry_count
                    )  # Exponential backoff
                    continue
                logger.error(f"Database error: {e}")
                raise
    finally:
        await session.close()


# Log connection pool events for debugging
@event.listens_for(async_engine.sync_engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checked out from pool")


@event.listens_for(async_engine.sync_engine, "checkin")
def checkin(dbapi_connection, connection_record):
    logger.debug("Database connection returned to pool")


# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(sync_engine)


async def create_db_and_tables_async():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Initialize database
async def init_db():
    await create_db_and_tables_async()
    # Add initial data if needed
