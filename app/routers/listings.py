from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from db.session import get_db
from schemas.listing import ListingCreate, ListingResponse, ListingUpdate, ImageUploadResponse
from services.listing import ListingService
from services.auth import AuthService
from models import User

router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return AuthService.get_current_user(db, credentials.credentials)

@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload image to Cloudinary"""
    return ListingService.upload_image(file)

@router.post("", response_model=ListingResponse)
async def create_listing(
    listing_data: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new listing"""
    return ListingService.create_listing(db, listing_data, current_user)

@router.get("", response_model=List[ListingResponse])
async def get_listings(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get listings with optional filtering"""
    return ListingService.get_listings(db, category, search, skip, limit)

@router.get("/my-listings", response_model=List[ListingResponse])
async def get_my_listings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's listings"""
    return ListingService.get_user_listings(db, current_user)

@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get listing by ID"""
    return ListingService.get_listing_by_id(db, listing_id)

@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    listing_data: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a listing"""
    return ListingService.update_listing(db, listing_id, listing_data, current_user)

@router.put("/{listing_id}/toggle", response_model=ListingResponse)
async def toggle_listing_status(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle listing active status"""
    return ListingService.toggle_listing_status(db, listing_id, current_user)