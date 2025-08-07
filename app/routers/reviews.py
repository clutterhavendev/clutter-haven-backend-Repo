from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from schemas.reviews import ReviewCreate, ReviewResponse, ReviewUpdate
from services.auth import AuthService
from models import User, Review, Order, Listing, Vendor

router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return AuthService.get_current_user(db, credentials.credentials)

@router.post("", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new review"""
    # Verify buyer has purchased from this vendor
    order_exists = db.query(Order).join(Listing).join(Vendor).filter(
        Order.buyer_id == current_user.id,
        Vendor.id == review_data.vendor_id,
        Order.status == "delivered"
    ).first()
    
    if not order_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review vendors you've purchased from"
        )
    
    # Check if review already exists
    existing_review = db.query(Review).filter(
        Review.buyer_id == current_user.id,
        Review.vendor_id == review_data.vendor_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this vendor"
        )
    
    review = Review(
        buyer_id=current_user.id,
        vendor_id=review_data.vendor_id,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.utcnow()
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/vendor/{vendor_id}", response_model=List[ReviewResponse])
async def get_vendor_reviews(vendor_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a vendor"""
    return db.query(Review).filter(Review.vendor_id == vendor_id).all()

@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reviews given by current user"""
    return db.query(Review).filter(Review.buyer_id == current_user.id).all()

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.buyer_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    update_data = review_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    return review

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.buyer_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}