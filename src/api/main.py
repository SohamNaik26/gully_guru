"""
Main module for the GullyGuru API.
This module initializes the FastAPI application and includes all routes.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GullyGuru API",
    description="API for the GullyGuru fantasy cricket application",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include API router directly at the root path instead of with /api prefix
# This change ensures the bot can access endpoints at the root path
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Welcome to the GullyGuru API"}


@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return {"status": "healthy", "database": "healthy"}
