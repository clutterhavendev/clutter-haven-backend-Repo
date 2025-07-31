from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
