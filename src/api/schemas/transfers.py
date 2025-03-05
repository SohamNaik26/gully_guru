from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class TransferWindowBase(BaseModel):
    week_number: int
    start_time: datetime
    end_time: datetime
    status: str

class TransferWindowCreate(TransferWindowBase):
    pass

class TransferWindowResponse(TransferWindowBase):
    id: int

class TransferListingBase(BaseModel):
    player_id: int
    min_price: Decimal

class TransferListingCreate(TransferListingBase):
    pass

class TransferListingResponse(TransferListingBase):
    id: int
    transfer_window_id: int
    seller_id: int
    status: str
    created_at: datetime

class TransferBidBase(BaseModel):
    listing_id: int
    bid_amount: Decimal

class TransferBidCreate(TransferBidBase):
    pass

class TransferBidResponse(TransferBidBase):
    id: int
    bidder_id: int
    status: str
    is_free_bid: bool
    created_at: datetime 