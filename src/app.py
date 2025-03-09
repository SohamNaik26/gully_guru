import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.db.init import init_db
from src.api.routes import api_router  # Import the API router

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
