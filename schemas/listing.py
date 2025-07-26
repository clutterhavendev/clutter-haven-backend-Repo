from pydantic import BaseModel
from typing import Optional, List

class ListingCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str
    condition: str
    is_bundle: bool = False

class ListingOut(ListingCreate):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
