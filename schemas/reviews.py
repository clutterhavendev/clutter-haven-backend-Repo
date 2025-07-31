from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating between 1 and 5")
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    listing_id: int

class ReviewOut(ReviewBase):
    id: int
    user_id: int
    listing_id: int
    created_at: datetime

    class Config:
        orm_mode = True
