from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ReviewCreate, ReviewOut
from services import create_review, get_reviews_for_listing, delete_review
from deps.current_user import get_current_user
from db.session import SessionLocal
from models.user import User
from models.reviews import Review
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST a new review
@router.post("/", response_model=ReviewOut)
def submit_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_review(review_data, db, current_user.id)

# GET all reviews for a listing
@router.get("/listing/{listing_id}", response_model=List[ReviewOut])
def listing_reviews(
    listing_id: int,
    db: Session = Depends(get_db),
):
    return get_reviews_for_listing(listing_id, db)

# Delete Review
@router.delete("/{review_id}")
def remove_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_review(
        review_id,
        db,
        current_user.id,
        is_admin=current_user.is_admin  # Check admin privileges
    )


# GET all reviews (admin only)
@router.get("/admin/all", response_model=List[ReviewOut])
def admin_all_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return db.query(Review).all()

# Admin DELETE any review
@router.delete("/admin/{review_id}")
def admin_delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")

    return delete_review(review_id, db, user_id=current_user.id, is_admin=True)
