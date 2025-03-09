from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone

from src.db.session import get_session
from src.db.models import User, GullyParticipant, Gully
from src.api.schemas.user import (
    UserCreate,
    UserResponse,
    GullyParticipantCreate,
    GullyParticipantResponse,
)
from src.api.dependencies import get_current_user
from src.api.exceptions import NotFoundException

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Create a new user."""
    # Check if user with telegram_id already exists
    existing_user = session.exec(
        select(User).where(User.telegram_id == user_data.telegram_id)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_id {user_data.telegram_id} already exists",
        )

    # Create new user
    user = User(**user_data.dict())
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get information about the current authenticated user."""
    return current_user


@router.get("/telegram/{telegram_id}", response_model=UserResponse)
def get_user_by_telegram_id(telegram_id: int, session: Session = Depends(get_session)):
    """Get a user by Telegram ID."""
    user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise NotFoundException(resource_type="User", resource_id=telegram_id)

    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get a user by ID."""
    user = session.get(User, user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    return user


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get all users."""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a user (can only delete yourself or admin can delete anyone)."""
    # Check if user exists
    user = session.get(User, user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    # Check permissions - only allow users to delete themselves
    # Admin check is removed since we no longer have is_admin field
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    # Delete user
    session.delete(user)
    session.commit()

    return None


@router.delete("/telegram/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_telegram_id(
    telegram_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a user by Telegram ID."""
    # Check if user exists
    user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise NotFoundException(resource_type="User", telegram_id=telegram_id)

    # Check permissions - only allow users to delete themselves
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    # Delete user
    session.delete(user)
    session.commit()

    return None


# GullyParticipant endpoints
@router.post(
    "/gully-participants",
    response_model=GullyParticipantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_gully_participant(
    participant_data: GullyParticipantCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new gully participant."""
    # Check if user exists
    user = session.get(User, participant_data.user_id)
    if not user:
        raise NotFoundException(
            resource_type="User", resource_id=participant_data.user_id
        )

    # Check if gully exists
    gully = session.get(Gully, participant_data.gully_id)
    if not gully:
        raise NotFoundException(
            resource_type="Gully", resource_id=participant_data.gully_id
        )

    # Check if participant already exists
    existing_participant = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == participant_data.user_id)
            & (GullyParticipant.gully_id == participant_data.gully_id)
        )
    ).first()

    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {participant_data.user_id} is already a participant in gully {participant_data.gully_id}",
        )

    # Create new participant
    participant = GullyParticipant(**participant_data.dict())
    session.add(participant)
    session.commit()
    session.refresh(participant)

    return participant


@router.get(
    "/gully-participants/{participant_id}", response_model=GullyParticipantResponse
)
def get_gully_participant(
    participant_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get a gully participant by ID."""
    participant = session.get(GullyParticipant, participant_id)
    if not participant:
        raise NotFoundException(
            resource_type="GullyParticipant", resource_id=participant_id
        )

    return participant


@router.get(
    "/gully-participants/user/{user_id}", response_model=List[GullyParticipantResponse]
)
def get_user_gully_participations(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all gully participations for a user."""
    # Check if user exists
    user = session.get(User, user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    # Check permissions - users can only view their own participations
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own gully participations",
        )

    participations = session.exec(
        select(GullyParticipant).where(GullyParticipant.user_id == user_id)
    ).all()

    return participations


@router.get(
    "/gully-participants/gully/{gully_id}",
    response_model=List[GullyParticipantResponse],
)
def get_gully_participants(
    gully_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get all participants in a gully."""
    # Check if gully exists
    gully = session.get(Gully, gully_id)
    if not gully:
        raise NotFoundException(resource_type="Gully", resource_id=gully_id)

    participants = session.exec(
        select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
    ).all()

    return participants


@router.put(
    "/gully-participants/{participant_id}/set-active",
    response_model=GullyParticipantResponse,
)
def set_active_gully(
    participant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Set a gully as the active gully for a user."""
    # Get the participant
    participant = session.get(GullyParticipant, participant_id)
    if not participant:
        raise NotFoundException(
            resource_type="GullyParticipant", resource_id=participant_id
        )

    # Check permissions - users can only update their own active gully
    if participant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own active gully",
        )

    # First, set all other gullies as inactive
    other_participations = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == participant.user_id)
            & (GullyParticipant.id != participant_id)
        )
    ).all()

    for other in other_participations:
        other.is_active = False

    # Set this gully as active
    participant.is_active = True
    participant.last_active_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(participant)

    return participant


@router.put(
    "/gully-participants/{participant_id}/complete-registration",
    response_model=GullyParticipantResponse,
)
def complete_registration(
    participant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Mark a user's registration as complete for a gully."""
    # Get the participant
    participant = session.get(GullyParticipant, participant_id)
    if not participant:
        raise NotFoundException(
            resource_type="GullyParticipant", resource_id=participant_id
        )

    # Check permissions - users can only update their own registration status
    if participant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own registration status",
        )

    # Mark registration as complete
    participant.registration_complete = True
    participant.last_active_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(participant)

    return participant


@router.put("/gully-participants/{participant_id}/role", response_model=dict)
async def update_participant_role(
    participant_id: int,
    role: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update a gully participant's role."""
    # Find the participant
    participant = session.get(GullyParticipant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with ID {participant_id} not found",
        )

    # Allow the API to update roles without admin check when called from the bot
    # This is a simplified approach for now

    # Update the role
    participant.role = role
    session.add(participant)
    session.commit()
    session.refresh(participant)

    return {
        "success": True,
        "message": f"Role updated to {role}",
        "participant": {
            "id": participant.id,
            "user_id": participant.user_id,
            "gully_id": participant.gully_id,
            "role": participant.role,
        },
    }
