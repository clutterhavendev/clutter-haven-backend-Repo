from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

# ORDER SCHEMAS 

class OrderCreate(BaseModel):
    listing_id: int

class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    listing_id: int
    status: str
    ordered_at: datetime
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v


# PAYMENT SCHEMAS 
class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# DELIVERY SCHEMAS 

class DeliveryRequestCreate(BaseModel):
    order_id: int
    dispatch_option: str
    logistics_partner: Optional[str] = None
    
    @field_validator('dispatch_option')
    @classmethod
    def validate_dispatch_option(cls, v):
        if v not in ['pickup', 'drop-off']:
            raise ValueError('dispatch_option must be either pickup or drop-off')
        return v

class DeliveryRequestResponse(BaseModel):
    id: int
    order_id: int
    dispatch_option: str
    logistics_partner: Optional[str]
    delivery_status: str
    confirmed_by_buyer: bool
    
    class Config:
        from_attributes = True