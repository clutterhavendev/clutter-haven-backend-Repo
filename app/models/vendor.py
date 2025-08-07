from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class VendorPlan(Base):
    __tablename__ = "vendor_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 'basic' or 'premium'
    monthly_fee = Column(DECIMAL(10, 2), nullable=False)
    remittance_rate = Column(DECIMAL(5, 2), nullable=False)  # Percentage
    max_listings_per_month = Column(Integer, nullable=False)
    visibility_boost = Column(Boolean, default=False)
    
    # Relationships
    vendors = relationship("Vendor", back_populates="plan")

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("vendor_plans.id"), nullable=False)
    verification_status = Column(String, default="pending")  # 'pending', 'verified', 'rejected'
    id_verified = Column(Boolean, default=False)
    location_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="vendor_profile")
    plan = relationship("VendorPlan", back_populates="vendors")
    listings = relationship("Listing", back_populates="vendor")
    reviews_received = relationship("Review", back_populates="vendor")