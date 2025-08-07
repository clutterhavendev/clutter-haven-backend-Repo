from sqlalchemy.orm import Session
from app.models.vendor import Vendor
from datetime import datetime

def register_vendor(db: Session, user_id: int, plan_id: int):
    existing = db.query(Vendor).filter_by(user_id=user_id).first()
    if existing:
        return existing  # return existing profile if already registered

    vendor = Vendor(
        user_id=user_id,
        plan_id=plan_id,
        verification_status="pending",
        id_verified=False,
        location_verified=False,
        created_at=datetime.utcnow()
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

def update_verification_status(db: Session, vendor_id: int, status: str):
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    if not vendor:
        return None
    vendor.verification_status = status
    if status == "verified":
        vendor.id_verified = True
        vendor.location_verified = True
    db.commit()
    db.refresh(vendor)
    return vendor
