from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

#Vendor Plan
class VendorPlanResponse(BaseModel):
    id: int
    name: str
    monthly_fee: Decimal
    remittance_rate: Decimal
    max_listings_per_month: int
    visibility_boost: bool
    
    class Config:
        from_attributes = True

#Vendor Schema
class VendorResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    verification_status: str
    id_verified: bool
    location_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class VendorVerificationUpdate(BaseModel):
    id_verified: bool
    location_verified: bool

class VendorPlanUpdate(BaseModel):
    plan_id: int