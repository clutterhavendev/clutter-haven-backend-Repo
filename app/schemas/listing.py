from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime

class ListingCreate(BaseModel):
    title: str
    description: Optional[str]
    price: Decimal
    item_condition: str
    category: str
    image_url: Optional[str] = None


    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
            if v <= 0:
                 raise ValueError('Price must be greater than 0')
            return v
           
        
    
    @field_validator('item_condition')
    @classmethod
    def validate_condition(cls, v):
        valid_conditions = ['new', 'like_new', 'good', 'fair', 'poor']
        if v not in valid_conditions:
            raise ValueError(f'item_condition must be one of {valid_conditions}')
        return v

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    item_condition: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

class ListingResponse(BaseModel):
    id: int
    vendor_id: int
    title: str
    description: Optional[str]
    price: Decimal
    item_condition: str
    category: str
    image_url: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImageUploadResponse(BaseModel):
    image_url: str
    public_id: str