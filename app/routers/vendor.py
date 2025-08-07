from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from schemas.vendors import VendorPlanResponse, VendorResponse, VendorVerificationUpdate
from services.auth import AuthService
from models import User, Vendor, VendorPlan

router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return AuthService.get_current_user(db, credentials.credentials)

@router.get("/plans", response_model=List[VendorPlanResponse])
async def get_vendor_plans(db: Session = Depends(get_db)):
    """Get all vendor plans"""
    return db.query(VendorPlan).all()

@router.get("/me", response_model=VendorResponse)
async def get_my_vendor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's vendor profile"""
    if current_user.user_type != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can access vendor profiles"
        )
    
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    return vendor

@router.put("/verification", response_model=VendorResponse)
async def update_vendor_verification(
    verification_data: VendorVerificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update vendor verification status"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    vendor.id_verified = verification_data.id_verified
    vendor.location_verified = verification_data.location_verified
    
    if vendor.id_verified and vendor.location_verified:
        vendor.verification_status = "verified"
    else:
        vendor.verification_status = "pending"
    
    db.commit()
    db.refresh(vendor)
    return vendor