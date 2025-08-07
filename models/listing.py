# app/models/listing.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base
from models.listing import Listing

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    location = Column(String)
    category = Column(String)
    item_condition = Column(String)
    is_active = Column(Boolean, default=False)
    image_url = Column(String)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    created_at = datetime
    is_active = Column(Boolean, default=True) #Allows admin block/suspend a listing which make it invisible on the app

    owner = relationship("User", back_populates="listings")

    reviews = relationship("Review", back_populates="listing", cascade="all, delete")

