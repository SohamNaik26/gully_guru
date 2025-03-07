import os
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, select, create_engine
from typing import List, Optional
from src.db.models import User, Player, PlayerStats, UserPlayer
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models.api import PlayerCreate, UserPlayerCreate


load_dotenv()
YOLO_DATABASE_URL = os.getenv("YOLO_DATABASE_URL")
engine = create_engine(YOLO_DATABASE_URL)


def create_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(lifespan=app_lifespan)


# Define session dependency
def get_session():
    with Session(engine) as session:
        yield session


# Keep original sync endpoints for backward compatibility
@app.post("/users/", response_model=User)
async def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}


@app.get("/users/", response_model=List[User])
async def read_users(session: Session = Depends(get_session)):
    result = session.exec(select(User)).all()
    return result


@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int, user_update: User, session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/playerstats/", response_model=PlayerStats)
async def create_player_stat(
    stat: PlayerStats, session: Session = Depends(get_session)
):
    session.add(stat)
    session.commit()
    session.refresh(stat)
    return stat


@app.get("/playerstats/", response_model=List[PlayerStats])
async def read_player_stats(session: Session = Depends(get_session)):
    result = session.exec(select(PlayerStats)).all()
    return result


@app.get("/playerstats/{stat_id}", response_model=PlayerStats)
async def read_player_stat(stat_id: int, session: Session = Depends(get_session)):
    stat = session.get(PlayerStats, stat_id)
    if not stat:
        raise HTTPException(status_code=404, detail="PlayerStat not found")
    return stat


# Keep the async functions for the async part of the API
async def get_player(session: AsyncSession, player_id: int) -> Optional[Player]:
    """Get a player by ID."""
    result = await session.execute(select(Player).where(Player.id == player_id))
    return result.scalar_one_or_none()


async def get_players(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    team: Optional[str] = None,
    player_type: Optional[str] = None,
    season: Optional[int] = None,
) -> List[Player]:
    """Get players with optional filtering."""
    query = select(Player)

    if team:
        query = query.where(Player.team == team)
    if player_type:
        query = query.where(Player.player_type == player_type)
    if season:
        query = query.where(Player.season == season)

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def create_player(session: AsyncSession, player: PlayerCreate) -> Player:
    """Create a new player."""
    db_player = Player(**player.dict())
    session.add(db_player)
    await session.commit()
    await session.refresh(db_player)
    return db_player


async def get_user_player(
    session: AsyncSession, user_player_id: int
) -> Optional[UserPlayer]:
    """Get a user-player link by ID."""
    result = await session.execute(
        select(UserPlayer).where(UserPlayer.id == user_player_id)
    )
    return result.scalar_one_or_none()


async def get_user_players(
    session: AsyncSession,
    user_id: Optional[int] = None,
    gully_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[UserPlayer]:
    """Get user-player links with optional filtering."""
    query = select(UserPlayer)

    if user_id:
        query = query.where(UserPlayer.user_id == user_id)
    if gully_id:
        query = query.where(UserPlayer.gully_id == gully_id)

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def create_user_player(
    session: AsyncSession, user_player: UserPlayerCreate
) -> UserPlayer:
    """Create a new user-player link."""
    # Check if player is already assigned
    result = await session.execute(
        select(UserPlayer).where(UserPlayer.player_id == user_player.player_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError(
            f"Player ID {user_player.player_id} is already assigned to user ID {existing.user_id}"
        )

    db_user_player = UserPlayer(**user_player.dict())
    session.add(db_user_player)
    await session.commit()
    await session.refresh(db_user_player)
    return db_user_player


async def get_user_team(
    session: AsyncSession, user_id: int, gully_id: Optional[int] = None
) -> List[Player]:
    """Get all players owned by a user."""
    query = select(Player).join(UserPlayer).where(UserPlayer.user_id == user_id)

    if gully_id:
        query = query.where(UserPlayer.gully_id == gully_id)

    result = await session.execute(query)
    return result.scalars().all()
