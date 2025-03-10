from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.db.models import User, GullyParticipant
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/gully/{gully_id}/admins")
async def get_gully_admins_endpoint(
    gully_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all admins for a gully."""
    # Query for all admin participants in the gully
    query = select(GullyParticipant).where(
        (GullyParticipant.gully_id == gully_id)
        & (GullyParticipant.role.in_(["admin", "owner"]))
    )

    result = await session.execute(query)
    admin_participants = result.scalars().all()

    # Get the user details for each admin
    admin_users = []
    for participant in admin_participants:
        user = await session.get(User, participant.user_id)
        if user:
            admin_users.append(
                {
                    "user_id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": participant.role,
                }
            )

    return admin_users
