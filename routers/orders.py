from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import order as order_model
from schemas import order as order_schema

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=order_schema.OrderResponse)
def create_order(order: order_schema.OrderCreate, db: Session = Depends(get_db)):
    db_order = order_model.Order(
        buyer_id=1,  # Assume user is authenticated
        listing_id=order.listing_id,
        amount=order.amount,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order