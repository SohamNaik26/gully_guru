from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta

from src.models.gully import Gully
from src.models.gully_participant import GullyParticipant
from src.models.user import User
from src.database.session import get_session
from src.api.schemas.gullies import (
    GullyCreate,
    GullyResponse,
    GullyParticipantCreate,
    GullyParticipantResponse,
)
from src.api.dependencies import get_current_user

router = APIRouter()


@router.post("/gullies", response_model=GullyResponse)
async def create_gully(
    gully_data: GullyCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new gully instance."""
    # Check if group already has a gully
    existing_gully = session.exec(
        select(Gully).where(Gully.telegram_group_id == gully_data.telegram_group_id)
    ).first()

    if existing_gully:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This group already has an active gully",
        )

    # Create new gully
    new_gully = Gully(
        name=gully_data.name,
        telegram_group_id=gully_data.telegram_group_id,
        status="pending",
        start_date=gully_data.start_date,
        end_date=gully_data.end_date,
    )

    session.add(new_gully)
    session.commit()
    session.refresh(new_gully)

    return new_gully


@router.get("/gullies", response_model=List[GullyResponse])
async def get_gullies(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all gullies."""
    gullies = session.exec(select(Gully)).all()
    return gullies


@router.get("/gullies/{gully_id}", response_model=GullyResponse)
async def get_gully(
    gully_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a specific gully by ID."""
    gully = session.exec(select(Gully).where(Gully.id == gully_id)).first()

    if not gully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gully not found"
        )

    return gully


@router.get("/gullies/group/{group_id}", response_model=GullyResponse)
async def get_gully_by_group(
    group_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a gully by Telegram group ID."""
    gully = session.exec(
        select(Gully).where(Gully.telegram_group_id == group_id)
    ).first()

    if not gully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No gully found for this group",
        )

    return gully


@router.post("/gullies/{gully_id}/join", response_model=GullyParticipantResponse)
async def join_gully(
    gully_id: int,
    participant_data: GullyParticipantCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Join a gully as a participant."""
    # Check if gully exists
    gully = session.exec(select(Gully).where(Gully.id == gully_id)).first()

    if not gully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gully not found"
        )

    # Check if user already joined this gully
    existing_participant = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.user_id == participant_data.user_id)
        )
    ).first()

    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already joined this gully",
        )

    # Create new participant
    new_participant = GullyParticipant(
        gully_id=gully_id,
        user_id=participant_data.user_id,
        team_name=participant_data.team_name,
        budget=100.0,  # Default starting budget
        points=0,
    )

    session.add(new_participant)
    session.commit()
    session.refresh(new_participant)

    return new_participant


@router.get(
    "/gullies/{gully_id}/participants", response_model=List[GullyParticipantResponse]
)
async def get_gully_participants(
    gully_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all participants in a gully."""
    participants = session.exec(
        select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
    ).all()

    return participants


@router.get("/users/{user_id}/gullies", response_model=List[GullyResponse])
async def get_user_gullies(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all gullies a user is participating in."""
    gullies = session.exec(
        select(Gully).join(GullyParticipant).where(GullyParticipant.user_id == user_id)
    ).all()

    return gullies
