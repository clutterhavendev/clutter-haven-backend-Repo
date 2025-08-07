from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from db.session import get_db
from schemas.users import WalletResponse, WalletTopup
from services.auth import AuthService
from models import User, Wallet

router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return AuthService.get_current_user(db, credentials.credentials)

@router.get("/me", response_model=WalletResponse)
async def get_my_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's wallet"""
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    return wallet

@router.post("/topup")
async def topup_wallet(
    topup_data: WalletTopup,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Top up wallet balance"""
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    wallet.balance += topup_data.amount
    wallet.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "message": f"Wallet topped up with ${topup_data.amount}",
        "new_balance": wallet.balance
    }