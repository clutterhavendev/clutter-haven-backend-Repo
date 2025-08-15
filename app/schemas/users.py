from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# USER SCHEMAS

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['buyer', 'seller', 'admin']:
            raise ValueError('role must be either buyer, seller, or admin')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    role: str
    is_verified: bool
    is_id_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class VerificationCodeRequest(BaseModel):
    type: str # 'phone' or 'email'

class VerificationCodeCheck(BaseModel):
    code: str

class LocationUpdate(BaseModel):
    location: str

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str] = []

    class Config:
        from_attributes = True

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

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