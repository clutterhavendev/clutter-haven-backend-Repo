from pydantic import BaseModel
from typing import Optional
from enum import Enum
import datetime

class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    delivered = "delivered"
    refunded = "refunded"

class OrderCreate(BaseModel):
    listing_id: int
    amount: float

class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    listing_id: int
    amount: float
    status: OrderStatus
    created_at: datetime.datetime

    class Config:
        orm_mode = True