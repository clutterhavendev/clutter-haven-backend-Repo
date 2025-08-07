from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from services.auth import AuthService
from models import User, Order, Listing, Wallet, Payment, Vendor, VendorPlan

router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return AuthService.get_current_user(db, credentials.credentials)

@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    if current_user.user_type != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create orders"
        )
    
    listing = db.query(Listing).filter(
        Listing.id == order_data.listing_id,
        Listing.is_active == True
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or inactive"
        )
    
    # Check buyer's wallet balance
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if wallet.balance < listing.price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance"
        )
    
    # Create order
    order = Order(
        buyer_id=current_user.id,
        listing_id=listing.id,
        status="pending",
        ordered_at=datetime.utcnow()
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Deduct from buyer's wallet (escrow)
    wallet.balance -= listing.price
    wallet.updated_at = datetime.utcnow()
    
    # Create payment record
    payment = Payment(
        order_id=order.id,
        amount=listing.price,
        payment_method="wallet",
        status="completed",
        created_at=datetime.utcnow()
    )
    
    db.add(payment)
    db.commit()
    
    return order

@router.get("/my-purchases", response_model=List[OrderResponse])
async def get_my_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's purchases"""
    return db.query(Order).filter(Order.buyer_id == current_user.id).all()

@router.get("/my-sales", response_model=List[OrderResponse])
async def get_my_sales(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's sales"""
    if current_user.user_type != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can view sales"
        )
    
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    return db.query(Order).join(Listing).filter(Listing.vendor_id == vendor.id).all()

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check authorization
    listing = db.query(Listing).filter(Listing.id == order.listing_id).first()
    vendor = db.query(Vendor).filter(Vendor.id == listing.vendor_id).first()
    
    if order.buyer_id != current_user.id and vendor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this order"
        )
    
    order.status = status_data.status
    if status_data.status == "delivered":
        order.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    return order

@router.put("/{order_id}/confirm-delivery")
async def confirm_delivery(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm delivery and release payment to seller"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.buyer_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != "shipped":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be shipped before confirmation"
        )
    
    # Update order status
    order.status = "delivered"
    order.delivered_at = datetime.utcnow()
    
    # Release payment to seller
    listing = db.query(Listing).filter(Listing.id == order.listing_id).first()
    vendor = db.query(Vendor).filter(Vendor.id == listing.vendor_id).first()
    seller_wallet = db.query(Wallet).filter(Wallet.user_id == vendor.user_id).first()
    
    # Calculate seller earnings (after platform fee)
    vendor_plan = db.query(VendorPlan).filter(VendorPlan.id == vendor.plan_id).first()
    seller_earnings = listing.price * (vendor_plan.remittance_rate / 100)
    
    seller_wallet.balance += seller_earnings
    seller_wallet.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Delivery confirmed, payment released to seller"}