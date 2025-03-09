from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.db.session import get_session
from src.db.models import User, Gully, GullyParticipant
from src.api.dependencies import get_current_user

# Remove imports from gully_service
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


async def get_all_gullies(session: Session) -> List[Dict[str, Any]]:
    """
    Get all gullies.

    Args:
        session: Database session

    Returns:
        List of all gullies
    """
    gullies = session.exec(select(Gully)).all()

    return [
        {
            "id": gully.id,
            "name": gully.name,
            "telegram_group_id": gully.telegram_group_id,
            "status": gully.status,
            "start_date": gully.start_date.isoformat(),
            "end_date": gully.end_date.isoformat(),
        }
        for gully in gullies
    ]


async def get_gully_by_chat_id(
    telegram_group_id: int, session: Session
) -> Optional[Dict[str, Any]]:
    """
    Get a gully by its Telegram chat ID.

    Args:
        telegram_group_id: The Telegram group ID
        session: Database session

    Returns:
        The gully data or None if not found
    """
    gully = session.exec(
        select(Gully).where(Gully.telegram_group_id == telegram_group_id)
    ).first()

    if not gully:
        return None

    return {
        "id": gully.id,
        "name": gully.name,
        "telegram_group_id": gully.telegram_group_id,
        "status": gully.status,
        "start_date": gully.start_date.isoformat(),
        "end_date": gully.end_date.isoformat(),
    }


async def create_gully(
    name: str,
    telegram_group_id: int,
    start_date: str,
    end_date: str,
    session: Session,
) -> Optional[Dict[str, Any]]:
    """
    Create a new gully.

    Args:
        name: The name of the gully
        telegram_group_id: The Telegram group ID
        start_date: The start date (YYYY-MM-DD)
        end_date: The end date (YYYY-MM-DD)
        session: Database session

    Returns:
        The created gully or None if creation failed
    """
    try:
        # Check if a gully already exists for this group
        existing_gully = session.exec(
            select(Gully).where(Gully.telegram_group_id == telegram_group_id)
        ).first()

        if existing_gully:
            return {
                "id": existing_gully.id,
                "name": existing_gully.name,
                "telegram_group_id": existing_gully.telegram_group_id,
                "status": existing_gully.status,
                "start_date": existing_gully.start_date.isoformat(),
                "end_date": existing_gully.end_date.isoformat(),
            }

        # Create a new gully
        new_gully = Gully(
            name=name,
            telegram_group_id=telegram_group_id,
            status="active",
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
        )

        session.add(new_gully)
        session.commit()
        session.refresh(new_gully)

        return {
            "id": new_gully.id,
            "name": new_gully.name,
            "telegram_group_id": new_gully.telegram_group_id,
            "status": new_gully.status,
            "start_date": new_gully.start_date.isoformat(),
            "end_date": new_gully.end_date.isoformat(),
        }
    except Exception as e:
        logger.error(f"Error creating gully: {e}")
        session.rollback()
        return None


async def add_user_to_gully(
    user_id: int, gully_id: int, role: str = "member", session: Session = None
) -> Optional[Dict[str, Any]]:
    """
    Add a user to a gully.

    Args:
        user_id: The user's ID
        gully_id: The gully ID
        role: The user's role in the gully (default: "member")
        session: Database session

    Returns:
        The created participant or None if creation failed
    """
    try:
        # Check if the user is already in the gully
        existing_participant = session.exec(
            select(GullyParticipant).where(
                (GullyParticipant.user_id == user_id)
                & (GullyParticipant.gully_id == gully_id)
            )
        ).first()

        if existing_participant:
            return {
                "id": existing_participant.id,
                "user_id": existing_participant.user_id,
                "gully_id": existing_participant.gully_id,
                "role": existing_participant.role,
                "is_active": existing_participant.is_active,
            }

        # Create a new participant
        new_participant = GullyParticipant(
            user_id=user_id,
            gully_id=gully_id,
            role=role,
            is_active=True,
            joined_via="added",
            last_active_at=datetime.now(),
            registration_complete=False,
        )

        session.add(new_participant)
        session.commit()
        session.refresh(new_participant)

        return {
            "id": new_participant.id,
            "user_id": new_participant.user_id,
            "gully_id": new_participant.gully_id,
            "role": new_participant.role,
            "is_active": new_participant.is_active,
        }
    except Exception as e:
        logger.error(f"Error adding user to gully: {e}")
        session.rollback()
        return None


async def get_gully_admins(gully_id: int, session: Session) -> List[Dict[str, Any]]:
    """
    Get all admins for a specific gully.

    Args:
        gully_id: The ID of the gully
        session: Database session

    Returns:
        List of admin users
    """
    # Find all participants with admin role in this gully
    admin_participants = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.role.in_(["admin", "owner"]))
        )
    ).all()

    # Get the user details for each admin
    admins = []
    for participant in admin_participants:
        user = session.get(User, participant.user_id)
        if user:
            admins.append(
                {
                    "user_id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": participant.role,
                }
            )

    return admins


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_gullies_endpoint(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get all gullies.
    """
    return await get_all_gullies(session)


@router.get("/{gully_id}", response_model=Dict[str, Any])
async def get_gully(
    gully_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific gully by ID.
    """
    gully = session.get(Gully, gully_id)
    if not gully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gully with ID {gully_id} not found",
        )

    return {
        "id": gully.id,
        "name": gully.name,
        "telegram_group_id": gully.telegram_group_id,
        "status": gully.status,
        "start_date": gully.start_date.isoformat(),
        "end_date": gully.end_date.isoformat(),
    }


@router.get("/group/{telegram_group_id}", response_model=Dict[str, Any])
async def get_gully_by_chat_id_endpoint(
    telegram_group_id: int,
    session: Session = Depends(get_session),
):
    """
    Get a gully by its Telegram group ID.
    """
    gully_data = await get_gully_by_chat_id(telegram_group_id, session)
    if not gully_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gully for group {telegram_group_id} not found",
        )

    return gully_data


@router.post("/", response_model=Dict[str, Any])
async def create_gully_endpoint(
    name: str,
    telegram_group_id: int,
    start_date: str,
    end_date: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new gully.
    """
    gully_data = await create_gully(
        name, telegram_group_id, start_date, end_date, session
    )

    if not gully_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create gully",
        )

    # Add the creator as an admin
    await add_user_to_gully(current_user.id, gully_data["id"], "owner", session)

    return gully_data


@router.get("/participants/{gully_id}", response_model=List[Dict[str, Any]])
async def get_gully_participants(
    gully_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get all participants in a gully.
    """
    # Check if the user is in this gully
    participant = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == current_user.id)
            & (GullyParticipant.gully_id == gully_id)
        )
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this gully",
        )

    # Get all participants
    participants_query = session.exec(
        select(GullyParticipant)
        .where(GullyParticipant.gully_id == gully_id)
        .offset(skip)
        .limit(limit)
    )

    participants = []
    for p in participants_query:
        user = session.get(User, p.user_id)
        if user:
            participants.append(
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "gully_id": p.gully_id,
                    "role": p.role,
                    "is_active": p.is_active,
                    "username": user.username,
                    "full_name": user.full_name,
                    "telegram_id": user.telegram_id,
                }
            )

    return participants


@router.get("/user-gullies/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_gullies(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get all gullies a user is participating in.
    """
    # Users can only view their own gully participations
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own gully participations",
        )

    # Get all gully participations for the user
    participations = session.exec(
        select(GullyParticipant).where(GullyParticipant.user_id == user_id)
    ).all()

    result = []
    for p in participations:
        gully = session.get(Gully, p.gully_id)
        if gully:
            result.append(
                {
                    "id": gully.id,
                    "name": gully.name,
                    "telegram_group_id": gully.telegram_group_id,
                    "status": gully.status,
                    "start_date": gully.start_date.isoformat(),
                    "end_date": gully.end_date.isoformat(),
                    "role": p.role,
                    "is_active": p.is_active,
                }
            )

    return result


@router.post("/participants/{gully_id}/{user_id}")
async def add_participant(
    gully_id: int,
    user_id: int,
    role: str = "member",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Add a user to a gully.
    """
    # Check if the current user is an admin in this gully
    admin_check = await get_gully_admins(gully_id, session)
    is_admin = any(admin["user_id"] == current_user.id for admin in admin_check)

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add participants",
        )

    # Add the user to the gully
    participant = await add_user_to_gully(user_id, gully_id, role, session)

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add user to gully",
        )

    return participant


@router.put("/participants/{gully_id}/{user_id}/activate")
async def activate_participant(
    gully_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Set a gully as the active gully for a user.
    """
    # Users can only change their own active gully
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only change your own active gully",
        )

    # Find the participant
    participant = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == user_id)
            & (GullyParticipant.gully_id == gully_id)
        )
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} is not a participant in gully {gully_id}",
        )

    # Deactivate all other gullies for this user
    other_participations = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == user_id)
            & (GullyParticipant.gully_id != gully_id)
        )
    ).all()

    for p in other_participations:
        p.is_active = False
        session.add(p)

    # Activate this gully
    participant.is_active = True
    participant.last_active_at = datetime.now()
    session.add(participant)
    session.commit()

    return {
        "success": True,
        "message": f"Gully {gully_id} is now active for user {user_id}",
    }
