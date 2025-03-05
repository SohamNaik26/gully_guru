from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class GullyBase(BaseModel):
    name: str
    telegram_group_id: int
    start_date: datetime
    end_date: datetime

class GullyCreate(GullyBase):
    pass

class GullyResponse(GullyBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

class GullyParticipantBase(BaseModel):
    user_id: int
    team_name: str

class GullyParticipantCreate(GullyParticipantBase):
    pass

class GullyParticipantResponse(GullyParticipantBase):
    id: int
    gully_id: int
    budget: Decimal
    points: int
    created_at: datetime
    updated_at: datetime 