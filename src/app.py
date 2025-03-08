import logging
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from typing import Dict, Any
from sqlmodel import Session, select

from src.db.init import init_db
from src.db.session import get_session
from src.db.models import User

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


# Direct API endpoints for user management
@app.get("/api/users/telegram/{telegram_id}")
async def get_user_by_telegram_id(
    telegram_id: int, session: Session = Depends(get_session)
):
    """Get a user by Telegram ID."""
    user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/users/", status_code=201)
async def create_user(
    user_data: Dict[str, Any], session: Session = Depends(get_session)
):
    """Create a new user."""
    # Check if user with telegram_id already exists
    if "telegram_id" not in user_data:
        raise HTTPException(status_code=400, detail="telegram_id is required")

    existing_user = session.exec(
        select(User).where(User.telegram_id == user_data["telegram_id"])
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail=f"User with telegram_id {user_data['telegram_id']} already exists",
        )

    # Create new user
    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@app.get("/api/users/{user_id}")
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get a user by ID."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/users/")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """Get all users."""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@app.patch("/api/users/telegram/{telegram_id}")
async def update_user_by_telegram_id(
    telegram_id: int, user_data: Dict[str, Any], session: Session = Depends(get_session)
):
    """Update a user by Telegram ID."""
    user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user
