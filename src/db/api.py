import os
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, select, create_engine
from typing import List
from src.db.models import User, IPLSchedule, PlayerStats
from dotenv import load_dotenv
from contextlib import asynccontextmanager


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


def get_session():
    with Session(engine) as session:
        yield session


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


@app.post("/iplschedule/", response_model=IPLSchedule)
async def create_ipl_schedule(
    schedule: IPLSchedule, session: Session = Depends(get_session)
):
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


@app.get("/iplschedule/", response_model=List[IPLSchedule])
async def read_ipl_schedules(session: Session = Depends(get_session)):
    result = session.exec(select(IPLSchedule)).all()
    return result


@app.get("/iplschedule/{schedule_id}", response_model=IPLSchedule)
async def read_ipl_schedule(schedule_id: int, session: Session = Depends(get_session)):
    schedule = session.get(IPLSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="IPLSchedule not found")
    return schedule


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
