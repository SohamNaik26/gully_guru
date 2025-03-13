from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.api.dependencies import get_current_user
from src.db.models.models import User, GullyParticipant
from src.db.session import get_session
from src.api.schemas.fantasy import (
    DraftPlayerCreate,
    DraftPlayerResponse,
    DraftSquadResponse,
    SquadSubmit,
    SubmissionStatusResponse,
    AuctionStartResponse,
    ContestPlayerResponse,
)
from src.api.services.fantasy import FantasyServiceClient
from src.api.factories.fantasy import (
    DraftPlayerResponseFactory,
    DraftSquadResponseFactory,
    SubmissionStatusResponseFactory,
    AuctionStartResponseFactory,
    ContestPlayerResponseFactory,
)

router = APIRouter()


# Squad Building Endpoints


@router.post("/draft-player", response_model=DraftPlayerResponse)
async def add_to_draft_squad(
    data: DraftPlayerCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Add a player to user's draft squad."""
    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.add_to_draft_squad(
        current_user.id, data.player_id, data.gully_id
    )
    return DraftPlayerResponseFactory.create_response(result)


@router.delete("/draft-player/{player_id}", response_model=DraftPlayerResponse)
async def remove_from_draft_squad(
    player_id: int,
    gully_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Remove a player from user's draft squad."""
    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.remove_from_draft_squad(
        current_user.id, player_id, gully_id
    )
    return DraftPlayerResponseFactory.create_response(result)


@router.get("/draft-squad", response_model=DraftSquadResponse)
async def get_draft_squad(
    gully_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get user's draft squad."""
    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.get_draft_squad(current_user.id, gully_id)
    return DraftSquadResponseFactory.create_response(result)


@router.post("/submit-squad", response_model=DraftPlayerResponse)
async def submit_squad(
    data: SquadSubmit,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Submit user's final squad."""
    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.submit_squad(current_user.id, data.gully_id)
    return DraftPlayerResponseFactory.create_response(result)


@router.get("/submission-status/{gully_id}", response_model=SubmissionStatusResponse)
async def get_submission_status(
    gully_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Check submission status for a Gully."""
    # Verify user is an admin for this gully
    result = await db.execute(
        select(GullyParticipant).where(
            GullyParticipant.user_id == current_user.id,
            GullyParticipant.gully_id == gully_id,
            GullyParticipant.role == "admin",
        )
    )
    participant = result.scalars().first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only gully admins can check submission status",
        )

    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.get_submission_status(gully_id)
    return SubmissionStatusResponseFactory.create_response(result)


@router.post("/start-auction/{gully_id}", response_model=AuctionStartResponse)
async def start_auction(
    gully_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Start auction for a Gully."""
    # Verify user is an admin for this gully
    result = await db.execute(
        select(GullyParticipant).where(
            GullyParticipant.user_id == current_user.id,
            GullyParticipant.gully_id == gully_id,
            GullyParticipant.role == "admin",
        )
    )
    participant = result.scalars().first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only gully admins can start auctions",
        )

    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.start_auction(gully_id)
    return AuctionStartResponseFactory.create_response(result)


@router.get("/contested-players/{gully_id}", response_model=ContestPlayerResponse)
async def get_contested_players(
    gully_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get contested players for a Gully."""
    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.get_contested_players(gully_id)
    return ContestPlayerResponseFactory.create_response(result)


@router.get("/uncontested-players/{gully_id}", response_model=ContestPlayerResponse)
async def get_uncontested_players(
    gully_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get uncontested players for a Gully."""
    fantasy_service = FantasyServiceClient(db)
    result = await fantasy_service.get_uncontested_players(gully_id)
    return ContestPlayerResponseFactory.create_response(result)
