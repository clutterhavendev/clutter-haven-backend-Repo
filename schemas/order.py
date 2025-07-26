from pydantic import BaseModel
from typing import List, Optional

class OrderItem(BaseModel):
    listing_id: int
    quantity: int

class OrderCreate(BaseModel):
    buyer_id: int
    items: List[OrderItem]

class OrderOut(BaseModel):
    id: int
    status: str
    items: List[OrderItem]

    class Config:
        orm_mode = True