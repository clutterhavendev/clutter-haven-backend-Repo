from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

# USER SCHEMAS

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    user_type: str
    
    @field_validator('user_type')
    @classmethod
    def validate_user_type(cls, v):
        if v not in ['buyer', 'seller']:
            raise ValueError('user_type must be either buyer or seller')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    user_type: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

# USER WALLET

class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WalletTopup(BaseModel):
    amount: Decimal
    
class Payment(BaseModel):
    amount: Decimal

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v