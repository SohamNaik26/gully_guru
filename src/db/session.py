import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/gullyguru")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create engines
engine = create_engine(DATABASE_URL, echo=False)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
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
async def get_async_session() -> AsyncSession:
    """
    Get a database session for asynchronous operations.
    
    Yields:
        AsyncSession: Async SQLModel session
    """
    async with AsyncSessionLocal() as session:
        yield session


# Create all tables (for development only)
def create_db_and_tables():
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)


# Initialize database (for testing and development)
def init_db():
    """Initialize the database with tables and initial data."""
    create_db_and_tables()
    # Add initial data if needed 