import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.db.init import init_db

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
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Fantasy Cricket API"}


# Import and include routers
# from src.api.routers import user_router, player_router, etc.
# app.include_router(user_router)
# app.include_router(player_router)
# etc.
