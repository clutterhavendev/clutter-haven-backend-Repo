from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

#  REVIEW SCHEMAS 

class ReviewCreate(BaseModel):
    vendor_id: int
    rating: int
    comment: Optional[str] = None
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewResponse(BaseModel):
    id: int
    buyer_id: int
    vendor_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    
    @field_validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v