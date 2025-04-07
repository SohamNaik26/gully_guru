import logging
import os
import sys
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

# Detect if we're running from src directory or root
if os.path.basename(os.getcwd()) == "src":
    # Running from src directory - use relative imports
    from db.init import init_db
    from db.session import get_session
    from db.models import User
    from api.routes import api_router
else:
    # Running from root directory - use absolute imports
    from src.db.init import init_db
    from src.db.session import get_session
    from src.db.models import User
    from src.api.routes import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the FastAPI application.
    """
    # Startup: Initialize database
    logger.info("Starting application...")
    await init_db()

    # Yield control to the application
    yield

    # Shutdown: Clean up resources
    logger.info("Shutting down application...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="GullyGuru Fantasy Cricket API",
    description="API for managing fantasy cricket teams, players, transfers, and more",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include the API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Fantasy Cricket API"}


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Health check endpoint to verify the API and database are working.

    Returns:
        dict: Health status information
    """
    try:
        # Check database connection
        result = await session.execute(select(User).limit(1))
        _ = result.scalars().first()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {"status": "ok", "database": db_status, "version": "1.0.0"}
