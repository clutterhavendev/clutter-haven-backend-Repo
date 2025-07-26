from pydantic import BaseModel

class ReviewCreate(BaseModel):
    reviewer_id: int
    reviewed_user_id: int
    rating: int
    comment: str

class ReviewOut(ReviewCreate):
    id: int

    class Config:
        orm_mode = True