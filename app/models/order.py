from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    status = Column(String, default="pending")  # 'pending', 'confirmed', 'shipped', 'delivered'
    ordered_at = Column(DateTime, default=datetime.now(timezone.utc))
    delivered_at = Column(DateTime, nullable=True)
    
    # Relationships
    buyer = relationship("User", back_populates="orders_as_buyer")
    listing = relationship("Listing", back_populates="orders")
    payments = relationship("Payment", back_populates="order")
    delivery_requests = relationship("DeliveryRequest", back_populates="order")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String, nullable=False)  # 'card' or 'wallet'
    status = Column(String, default="pending")  # 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.now (timezone.utc))
    
    # Relationships
    order = relationship("Order", back_populates="payments")

class DeliveryRequest(Base):
    __tablename__ = "delivery_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dispatch_option = Column(String, nullable=False)  # 'pickup' or 'drop-off'
    logistics_partner = Column(String, nullable=True)
    delivery_status = Column(String, default="pending")  # 'pending', 'in_transit', 'delivered'
    confirmed_by_buyer = Column(Boolean, default=False)
    
    # Relationships
    order = relationship("Order", back_populates="delivery_requests")