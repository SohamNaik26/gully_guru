"""
Participant routes for the GullyGuru API.
This module provides API endpoints for participant-related operations.
"""

import logging
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.db.session import get_session
from src.api.exceptions import NotFoundException
from src.api.schemas.participant import (
    ParticipantCreate,
    ParticipantResponse,
    ParticipantUpdate,
)
from src.api.services.participant import ParticipantService
from src.api.factories.participant import ParticipantResponseFactory
from src.api.schemas.common import SuccessResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/participants",
    tags=["Participants"],
)


@router.get("/", response_model=List[ParticipantResponse])
async def get_participants(
    gully_id: Optional[int] = Query(None, description="Filter by gully ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a list of participants with optional filtering.

    Args:
        gully_id: Optional filter by gully ID
        user_id: Optional filter by user ID
        skip: Number of participants to skip
        limit: Maximum number of participants to return
        session: Database session

    Returns:
        List[ParticipantResponse]: List of participants
    """
    participant_service = ParticipantService(session)
    participants = await participant_service.get_participants(
        gully_id=gully_id,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return [
        ParticipantResponseFactory.create_response(participant)
        for participant in participants
    ]


@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(
    participant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific participant by ID.

    Args:
        participant_id: Participant ID
        session: Database session

    Returns:
        ParticipantResponse: Participant details

    Raises:
        NotFoundException: If participant not found
    """
    participant_service = ParticipantService(session)
    participant = await participant_service.get_participant_by_id(participant_id)
    if not participant:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    return ParticipantResponseFactory.create_response(participant)


@router.post(
    "/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED
)
async def add_participant(
    participant_data: ParticipantCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Add a user to a gully.

    Args:
        participant_data: Participant data including user_id, gully_id, and role
        session: Database session

    Returns:
        ParticipantResponse: Created participant
    """
    participant_service = ParticipantService(session)

    # Check if user is already a participant
    existing_participant = await participant_service.get_participant(
        gully_id=participant_data.gully_id,
        user_id=participant_data.user_id,
    )
    if existing_participant:
        # Return existing participant instead of raising an error
        logger.info(
            f"User {participant_data.user_id} is already a participant in gully "
            f"{participant_data.gully_id}, returning existing participant"
        )
        return ParticipantResponseFactory.create_response(existing_participant)

    # Add participant
    participant = await participant_service.add_participant(
        gully_id=participant_data.gully_id,
        user_id=participant_data.user_id,
        role=participant_data.role,
        team_name=participant_data.team_name,
    )

    return ParticipantResponseFactory.create_response(participant)


@router.delete("/{participant_id}", response_model=SuccessResponse)
async def remove_participant(
    participant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Remove a participant by ID.

    Args:
        participant_id: Participant ID
        session: Database session

    Returns:
        SuccessResponse: Success response

    Raises:
        NotFoundException: If participant not found
    """
    participant_service = ParticipantService(session)

    # Get participant to check gully_id
    participant = await participant_service.get_participant_by_id(participant_id)
    if not participant:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    # Remove the participant
    removed = await participant_service.remove_participant(
        participant["gully_id"], participant["user_id"]
    )
    if not removed:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    return {
        "success": True,
        "message": f"Participant with ID {participant_id} removed",
    }


@router.put("/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: int,
    update_data: ParticipantUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update a participant's role or team name.

    Args:
        participant_id: Participant ID
        update_data: Update data including role and/or team_name
        session: Database session

    Returns:
        ParticipantResponse: Updated participant

    Raises:
        NotFoundException: If participant not found
    """
    participant_service = ParticipantService(session)

    # Get participant to check gully_id
    participant = await participant_service.get_participant_by_id(participant_id)
    if not participant:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    # Update participant
    updated_participant = await participant_service.update_participant(
        participant_id=participant_id,
        update_data=update_data.dict(exclude_unset=True),
    )

    if not updated_participant:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    return ParticipantResponseFactory.create_response(updated_participant)


@router.get("/user/{user_id}", response_model=List[ParticipantResponse])
async def get_user_participations(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get all gully participations for a user.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        List[ParticipantResponse]: List of participations

    Raises:
        NotFoundException: If user not found
    """
    participant_service = ParticipantService(session)
    participations = await participant_service.get_user_participations(user_id)

    return [
        ParticipantResponseFactory.create_response(participation)
        for participation in participations
    ]


@router.get("/gully/{gully_id}", response_model=List[ParticipantResponse])
async def get_gully_participants(
    gully_id: int,
    user_id: Optional[int] = Query(
        None, description="ID of the user requesting participants (optional)"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Get participants for a specific gully.

    Args:
        gully_id: Gully ID
        user_id: ID of the user requesting participants (optional)
        session: Database session

    Returns:
        List[ParticipantResponse]: List of participants
    """
    participant_service = ParticipantService(session)

    # Get the participants
    participants = await participant_service.get_participants(
        gully_id=gully_id, user_id=user_id
    )

    return [ParticipantResponseFactory.create_response(p) for p in participants]
