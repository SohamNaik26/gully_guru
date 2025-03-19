"""
Participant routes for the GullyGuru API.
This module provides API endpoints for participant-related operations.
"""

from fastapi import APIRouter, Depends, Path, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.api.dependencies.pagination import pagination_params, PaginationParams
from src.api.services.participant import ParticipantService
from src.api.schemas.participant import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
)
from src.api.schemas.pagination import PaginatedResponse
from src.api.exceptions import NotFoundException, handle_exceptions
from src.api.factories.participant import ParticipantResponseFactory

router = APIRouter(prefix="/participants", tags=["participants"])


@router.get("/", response_model=PaginatedResponse[ParticipantResponse])
@handle_exceptions
async def get_participants(
    gully_id: Optional[int] = Query(None, description="Filter by gully ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get participants with optional filtering by gully_id and/or user_id.

    Args:
        gully_id: Optional filter by gully ID
        user_id: Optional filter by user ID
        pagination: Pagination parameters
        db: Database session

    Returns:
        Paginated list of participants
    """
    participant_service = ParticipantService(db)
    participants = await participant_service.get_participants(
        gully_id=gully_id,
        user_id=user_id,
    )

    return ParticipantResponseFactory.create_response_list(participants)


@router.get("/{participant_id}", response_model=ParticipantResponse)
@handle_exceptions
async def get_participant_by_id(
    participant_id: int = Path(..., description="ID of the participant"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a participant by ID.

    Args:
        participant_id: ID of the participant
        db: Database session

    Returns:
        Participant details

    Raises:
        NotFoundException: If participant not found
    """
    participant_service = ParticipantService(db)
    participant = await participant_service.get_participant_by_id(participant_id)

    if not participant:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    return ParticipantResponseFactory.create_response(participant)


@router.get("/user/{user_id}/gully/{gully_id}", response_model=ParticipantResponse)
@handle_exceptions
async def get_participant_by_user_and_gully(
    user_id: int = Path(..., description="ID of the user"),
    gully_id: int = Path(..., description="ID of the gully"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a participant by user ID and gully ID.

    Args:
        user_id: ID of the user
        gully_id: ID of the gully
        db: Database session

    Returns:
        Participant details

    Raises:
        NotFoundException: If participant not found
    """
    participant_service = ParticipantService(db)
    participant = await participant_service.get_participant(gully_id, user_id)

    if not participant:
        raise NotFoundException(
            resource_type="Participant",
            resource_id=f"user {user_id} in gully {gully_id}",
        )

    return ParticipantResponseFactory.create_response(participant)


@router.post("/", response_model=ParticipantResponse, status_code=201)
@handle_exceptions
async def create_participant(
    participant: ParticipantCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a user to a gully.

    Args:
        participant: Participant data
        db: Database session

    Returns:
        Created participant details
    """
    participant_service = ParticipantService(db)
    new_participant = await participant_service.add_participant(
        gully_id=participant.gully_id,
        user_id=participant.user_id,
        role=participant.role,
        team_name=participant.team_name,
    )

    return ParticipantResponseFactory.create_response(new_participant)


@router.put("/{participant_id}", response_model=ParticipantResponse)
@handle_exceptions
async def update_participant(
    participant_id: int = Path(..., description="ID of the participant"),
    participant_update: ParticipantUpdate = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a participant's role or team name.

    Args:
        participant_id: ID of the participant
        participant_update: Updated participant data
        db: Database session

    Returns:
        Updated participant details

    Raises:
        NotFoundException: If participant not found
    """
    participant_service = ParticipantService(db)
    updated_participant = await participant_service.update_participant(
        participant_id=participant_id,
        update_data=participant_update.dict(exclude_unset=True),
    )

    if not updated_participant:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    return ParticipantResponseFactory.create_response(updated_participant)


@router.delete("/{participant_id}", status_code=204)
@handle_exceptions
async def delete_participant(
    participant_id: int = Path(..., description="ID of the participant"),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a participant.

    Args:
        participant_id: ID of the participant
        db: Database session

    Returns:
        None

    Raises:
        NotFoundException: If participant not found
    """
    participant_service = ParticipantService(db)
    # First get the participant to extract gully_id and user_id
    participant = await participant_service.get_participant_by_id(participant_id)

    if not participant:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    # Now remove the participant
    success = await participant_service.remove_participant(
        gully_id=participant["gully_id"],
        user_id=participant["user_id"],
    )

    if not success:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)

    return None


@router.get("/user/{user_id}", response_model=List[ParticipantResponse])
@handle_exceptions
async def get_user_participations(
    user_id: int = Path(..., description="ID of the user"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all participations for a user.

    Args:
        user_id: ID of the user
        db: Database session

    Returns:
        List of participations
    """
    participant_service = ParticipantService(db)
    participations = await participant_service.get_user_participations(user_id)

    return ParticipantResponseFactory.create_response_list(participations)


@router.get("/gully/{gully_id}", response_model=List[ParticipantResponse])
@handle_exceptions
async def get_gully_participants(
    gully_id: int = Path(..., description="ID of the gully"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all participants in a gully.

    Args:
        gully_id: ID of the gully
        db: Database session

    Returns:
        List of participants
    """
    participant_service = ParticipantService(db)
    participants, _ = await participant_service.get_participants(gully_id=gully_id)

    # Return participants directly as a list
    return participants
