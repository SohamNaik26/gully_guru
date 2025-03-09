from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.db.session import get_session
from src.db.models import User, Gully, GullyParticipant
from src.api.dependencies import get_current_user
from src.api.schemas.user import GullyParticipantCreate, GullyParticipantResponse

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
        List of gullies
    """
    gullies = session.exec(select(Gully)).all()
    return [
        {
            "id": gully.id,
            "name": gully.name,
            "telegram_group_id": gully.telegram_group_id,
            "status": gully.status,
        }
        for gully in gullies
    ]


async def get_gully_by_chat_id(
    telegram_group_id: int, session: Session
) -> Optional[Dict[str, Any]]:
    """
    Get a gully by Telegram chat ID.

    Args:
        telegram_group_id: Telegram group ID
        session: Database session

    Returns:
        Gully data or None if not found
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
    }


async def create_gully(
    name: str,
    telegram_group_id: int,
    session: Session,
) -> Optional[Dict[str, Any]]:
    """
    Create a new gully.

    Args:
        name: The name of the gully
        telegram_group_id: The Telegram group ID
        session: Database session

    Returns:
        The created gully data or None if creation failed
    """
    try:
        # Check if a gully with this Telegram group ID already exists
        existing_gully = session.exec(
            select(Gully).where(Gully.telegram_group_id == telegram_group_id)
        ).first()

        if existing_gully:
            return {
                "id": existing_gully.id,
                "name": existing_gully.name,
                "telegram_group_id": existing_gully.telegram_group_id,
                "status": existing_gully.status,
            }

        # Create a new gully
        new_gully = Gully(
            name=name,
            telegram_group_id=telegram_group_id,
        )
        session.add(new_gully)
        session.commit()
        session.refresh(new_gully)

        return {
            "id": new_gully.id,
            "name": new_gully.name,
            "telegram_group_id": new_gully.telegram_group_id,
            "status": new_gully.status,
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

        # Get user details to create a default team name
        user = session.get(User, user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return None

        # Get gully details
        gully = session.get(Gully, gully_id)
        if not gully:
            logger.error(f"Gully {gully_id} not found")
            return None

        # Create a default team name based on username and role
        default_team_name = f"{user.username}'s Team"
        if role == "owner":
            default_team_name = f"{gully.name} Owner"

        # Create a new participant
        new_participant = GullyParticipant(
            user_id=user_id,
            gully_id=gully_id,
            role=role,
            team_name=default_team_name,  # Add default team name
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
    Get a gully by ID.

    Args:
        gully_id: The gully ID
        session: Database session
        current_user: The current user

    Returns:
        The gully data
    """
    gully = session.get(Gully, gully_id)
    if not gully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gully not found"
        )

    return {
        "id": gully.id,
        "name": gully.name,
        "telegram_group_id": gully.telegram_group_id,
        "status": gully.status,
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
    gully_data: Dict[str, Any],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new gully.

    Args:
        gully_data: The gully data including name and telegram_group_id
        session: Database session
        current_user: The current user

    Returns:
        The created gully
    """
    if "name" not in gully_data or "telegram_group_id" not in gully_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="name and telegram_group_id are required",
        )

    name = gully_data["name"]
    telegram_group_id = gully_data["telegram_group_id"]

    # Check if a gully with this telegram_group_id already exists
    existing_gully = await get_gully_by_chat_id(telegram_group_id, session)
    if existing_gully:
        return existing_gully

    gully_result = await create_gully(name, telegram_group_id, session)

    if not gully_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create gully",
        )

    # Add the creator as an admin
    await add_user_to_gully(current_user.id, gully_result["id"], "owner", session)

    return gully_result


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
    Get all gullies for a user.

    Args:
        user_id: The user ID
        session: Database session
        current_user: The current user

    Returns:
        List of gullies for the user
    """
    # Check if the user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get all gullies for the user
    gully_participants = session.exec(
        select(GullyParticipant).where(GullyParticipant.user_id == user_id)
    ).all()

    gully_ids = [gp.gully_id for gp in gully_participants]
    gullies = session.exec(select(Gully).where(Gully.id.in_(gully_ids))).all()

    return [
        {
            "id": gully.id,
            "name": gully.name,
            "telegram_group_id": gully.telegram_group_id,
            "status": gully.status,
        }
        for gully in gullies
    ]


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
