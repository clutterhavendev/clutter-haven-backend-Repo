from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ListingCreate(BaseModel):
    title: str
    description: str
    price: float
    location: str
    category: str
    condition: str
    is_bundle: Optional[bool] = False
    media_url: Optional[str] = None  # URL or file path

class ListingOut(ListingCreate):
    id: int
    vendor_id: int

    class Config:
        orm_mode = True
