from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.api.routes import api_router
from src.api.exceptions import GullyGuruException
from src.db.session import create_db_and_tables
from src.utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")

# Initialize FastAPI app
app = FastAPI(
    title="GullyGuru API",
    description="Fantasy Cricket Platform API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")


# Exception handler
@app.exception_handler(GullyGuruException)
async def gullyguru_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    # Create tables if they don't exist (for development)
    if settings.ENVIRONMENT == "development":
        create_db_and_tables()
    logger.info("API started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
