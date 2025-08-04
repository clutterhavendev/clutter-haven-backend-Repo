from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import wallet as wallet_model
from schemas import wallet as wallet_schema

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.get("/{user_id}", response_model=wallet_schema.WalletResponse)
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    wallet = db.query(wallet_model.Wallet).filter(wallet_model.Wallet.user_id == user_id).first()
    if not wallet:
        wallet = wallet_model.Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet