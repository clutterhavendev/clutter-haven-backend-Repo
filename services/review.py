from sqlalchemy.orm import Session
from models.reviews import Review
from schemas.reviews import ReviewCreate
from fastapi import HTTPException

# Create a review
def create_review(data: ReviewCreate, db: Session, user_id: int):
    existing = db.query(Review).filter(
        Review.user_id == user_id,
        Review.listing_id == data.listing_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this listing.")

    review = Review(**data.model_dump(), user_id=user_id)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

# Get all reviews for a listing
def delete_review(review_id: int, db: Session, user_id: int, is_admin: bool = False):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.reviewer_id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    db.delete(review)
    db.commit()
    return {"message": "Review deleted"}
