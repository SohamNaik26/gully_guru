"""
Gully routes for the GullyGuru API.
This module provides API endpoints for gully-related operations.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional

from src.db.session import get_session
from src.api.exceptions import NotFoundException
from src.api.schemas.gully import (
    GullyCreate,
    GullyUpdate,
    GullyResponse,
    SuccessResponse,
    SubmissionStatusResponse,
)
from src.api.schemas.pagination import PaginatedResponse
from src.api.dependencies.database import get_db
from src.api.dependencies.pagination import pagination_params, PaginationParams
from src.api.dependencies.permissions import check_is_admin
from src.api.services.gully import GullyService
from src.api.services.participant import ParticipantService
from src.api.factories import GullyResponseFactory
from src.api.factories.gully import SubmissionStatusResponseFactory
from src.api.services.fantasy import FantasyService
from src.api.services.auction import AuctionService
from src.api.exceptions import handle_exceptions

# Configure logging
logger = logging.getLogger(__name__)


# Define helper functions for admin checks
async def is_gully_admin(user_id: int, gully_id: int, session: AsyncSession) -> bool:
    """
    Check if a user is an admin for a gully.

    Args:
        user_id: User ID to check
        gully_id: Gully ID to check
        session: Database session

    Returns:
        bool: True if user is admin in the gully, False otherwise
    """
    participant_service = ParticipantService(session)
    return await participant_service.is_admin(user_id, gully_id)


# Create router
router = APIRouter(
    prefix="/gullies",
    tags=["Gullies"],
)


def get_gully_service(
    db: AsyncSession = Depends(get_db),
) -> GullyService:
    """
    Get the gully service instance.

    Args:
        db: Database session

    Returns:
        GullyService instance
    """
    return GullyService(db)


def get_fantasy_service(
    db: AsyncSession = Depends(get_db),
) -> FantasyService:
    """
    Get the fantasy service instance.

    Args:
        db: Database session

    Returns:
        FantasyService instance
    """
    return FantasyService(db)


def get_auction_service(
    db: AsyncSession = Depends(get_db),
) -> AuctionService:
    """
    Get the auction service instance.

    Args:
        db: Database session

    Returns:
        AuctionService instance
    """
    return AuctionService(db)


# Gully endpoints
@router.get(
    "/",
    response_model=PaginatedResponse[GullyResponse],
    summary="Get a list of gullies with optional filtering",
)
@handle_exceptions
async def get_gullies(
    name: Optional[str] = Query(None, description="Filter by gully name"),
    status: Optional[str] = Query(None, description="Filter by gully status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    telegram_group_id: Optional[int] = Query(
        None, description="Filter by Telegram group ID"
    ),
    pagination: PaginationParams = Depends(pagination_params),
    gully_service: GullyService = Depends(get_gully_service),
):
    """
    Get a paginated list of gullies with optional filtering.

    Args:
        name: Optional filter by gully name
        status: Optional filter by gully status
        user_id: Optional filter by user ID
        telegram_group_id: Optional filter by Telegram group ID
        pagination: Pagination parameters
        gully_service: Gully service instance

    Returns:
        Paginated list of gullies
    """
    # Build filters
    filters = {}
    if name:
        filters["name"] = name
    if status:
        filters["status"] = status
    if telegram_group_id:
        filters["telegram_group_id"] = telegram_group_id

    # Call the updated service method
    gullies, total = await gully_service.get_gullies(
        filters=filters,
        user_id=user_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return {
        "items": [GullyResponseFactory.create_response(gully) for gully in gullies],
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/user/{user_id}", response_model=List[GullyResponse])
async def get_user_gullies(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get gullies for a specific user.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        List[GullyResponse]: List of gullies for the user

    Raises:
        NotFoundException: If user not found
    """
    gully_service = GullyService(session)
    gullies = await gully_service.get_user_gullies(user_id)

    if gullies is None:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    return [GullyResponseFactory.create_response(gully) for gully in gullies]


@router.get("/group/{telegram_group_id}", response_model=GullyResponse)
async def get_gully_by_group_id(
    telegram_group_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a gully by Telegram group ID.

    Args:
        telegram_group_id: Telegram group ID
        session: Database session

    Returns:
        GullyResponse: Gully details

    Raises:
        NotFoundException: If gully not found
    """
    gully_service = GullyService(session)
    gully = await gully_service.get_gully_by_group(telegram_group_id)
    if not gully:
        raise NotFoundException(resource_type="Gully", resource_id=telegram_group_id)
    return GullyResponseFactory.create_response(gully)


@router.post("/", response_model=GullyResponse, status_code=status.HTTP_201_CREATED)
async def create_gully(
    gully_data: GullyCreate,
    creator_id: Optional[int] = Query(
        None, description="ID of the user creating the gully"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new gully.

    Args:
        gully_data: Gully data including name and telegram_group_id
        creator_id: ID of the user creating the gully (optional for bot-created gullies)
        session: Database session

    Returns:
        GullyResponse: Created gully with ID and timestamps

    Raises:
        HTTPException: If gully with same group ID already exists
    """
    gully_service = GullyService(session)

    # Check if gully with same group ID already exists
    if hasattr(gully_data, "telegram_group_id") and gully_data.telegram_group_id:
        existing_gully = await gully_service.get_gully_by_group(
            gully_data.telegram_group_id
        )
        if existing_gully:
            # Return existing gully instead of raising an error
            logger.info(
                f"Gully with telegram_group_id {gully_data.telegram_group_id} already exists, returning existing gully"
            )
            return GullyResponseFactory.create_response(existing_gully)

    # Create gully with appropriate parameters based on what's available in gully_data
    gully_params = {
        "name": gully_data.name,
    }

    # Add creator_id if provided
    if creator_id is not None:
        gully_params["creator_id"] = creator_id
    elif hasattr(gully_data, "creator_id") and gully_data.creator_id is not None:
        gully_params["creator_id"] = gully_data.creator_id

    # Add optional parameters if they exist in the schema
    if hasattr(gully_data, "description"):
        gully_params["description"] = gully_data.description
    if hasattr(gully_data, "telegram_group_id"):
        gully_params["telegram_group_id"] = gully_data.telegram_group_id

    gully = await gully_service.create_gully(**gully_params)

    return GullyResponseFactory.create_response(gully)


@router.get("/{gully_id}", response_model=GullyResponse)
async def get_gully(
    gully_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a gully by ID.

    Args:
        gully_id: Gully ID
        session: Database session

    Returns:
        GullyResponse: Gully details

    Raises:
        NotFoundException: If gully not found
    """
    gully_service = GullyService(session)
    gully = await gully_service.get_gully(gully_id)
    if not gully:
        raise NotFoundException(resource_type="Gully", resource_id=gully_id)
    return GullyResponseFactory.create_response(gully)


@router.put("/{gully_id}", response_model=GullyResponse)
async def update_gully(
    gully_id: int,
    gully_data: GullyUpdate,
    user_id: Optional[int] = Query(
        None, description="ID of the user updating the gully"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a gully by ID.

    Args:
        gully_id: Gully ID
        gully_data: Gully data to update
        user_id: ID of the user updating the gully (optional for bot updates)
        session: Database session

    Returns:
        GullyResponse: Updated gully details

    Raises:
        NotFoundException: If gully not found
        HTTPException: If user is not an admin in the gully
    """
    gully_service = GullyService(session)

    # Check if user is admin in the gully (skip for bot updates)
    if user_id is not None:
        is_admin = await is_gully_admin(user_id, gully_id, session)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only gully admins can update gully details",
            )

    # Update gully
    gully = await gully_service.update_gully(
        gully_id, gully_data.dict(exclude_unset=True)
    )
    if not gully:
        raise NotFoundException(resource_type="Gully", resource_id=gully_id)

    return GullyResponseFactory.create_response(gully)


@router.put("/{gully_id}/status", response_model=SuccessResponse)
async def update_gully_status(
    gully_id: int,
    status: str = Query(..., description="New status for the gully"),
    user_id: Optional[int] = Query(
        None, description="ID of the user updating the gully status"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a gully's status.

    Args:
        gully_id: Gully ID
        status: New status
        user_id: ID of the user updating the gully status (optional for bot updates)
        session: Database session

    Returns:
        SuccessResponse: Success response

    Raises:
        HTTPException: If user is not an admin in the gully or update fails
    """
    gully_service = GullyService(session)

    # Check if user is admin in the gully (skip for bot updates)
    if user_id is not None:
        is_admin = await is_gully_admin(user_id, gully_id, session)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only gully admins can update the gully status",
            )

    # Update the gully status
    result = await gully_service.update_gully_status(gully_id, status)

    if isinstance(result, dict) and not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to update gully status"),
        )

    return {"success": True, "message": f"Gully status updated to {status}"}


@router.delete("/{gully_id}", response_model=SuccessResponse)
async def delete_gully(
    gully_id: int,
    user_id: Optional[int] = Query(
        None, description="ID of the user deleting the gully"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a gully by ID.

    Args:
        gully_id: Gully ID
        user_id: ID of the user deleting the gully (optional for bot operations)
        session: Database session

    Returns:
        SuccessResponse: Success response

    Raises:
        NotFoundException: If gully not found
        HTTPException: If user is not an admin in the gully
    """
    gully_service = GullyService(session)

    # Check if user is admin in the gully (skip for bot operations)
    if user_id is not None:
        is_admin = await is_gully_admin(user_id, gully_id, session)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only gully admins can delete the gully",
            )

    # Delete the gully
    deleted = await gully_service.delete_gully(gully_id)
    if not deleted:
        raise NotFoundException(resource_type="Gully", resource_id=gully_id)

    return {"success": True, "message": f"Gully with ID {gully_id} deleted"}


@router.get(
    "/{gully_id}/submission-status",
    response_model=SubmissionStatusResponse,
    summary="Get submission status for a gully",
)
async def get_gully_submission_status(
    gully_id: int = Path(..., description="ID of the gully"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Get the submission status for a gully.

    Args:
        gully_id: ID of the gully

    Returns:
        Submission status data
    """
    try:
        status_data = await fantasy_service.get_submission_status(gully_id)
        return SubmissionStatusResponseFactory.create_response(status_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
