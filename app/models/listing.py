# app/models/listing.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    item_condition = Column(String, nullable=False)  # 'new', 'used', etc.
    category = Column(String, nullable=False)
    image_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True) #Allows admin block/suspend a listing which make it invisible on the app

     # Relationships
    vendor = relationship("Vendor", back_populates="listings")
    orders = relationship("Order", back_populates="listing")