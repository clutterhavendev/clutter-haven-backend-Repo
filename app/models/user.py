from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime, timezone
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # 'buyer' or 'seller'
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_admin = Column(Boolean, default=False)  # ✅ Admin capability

    # Relationships
    vendor_profile = relationship("Vendor", back_populates="user", uselist=False)
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    orders_as_buyer = relationship("Order", back_populates="buyer")
    reviews_given = relationship("Review", back_populates="buyer")
    
class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(DECIMAL(10, 2), default=0.00)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="wallet")