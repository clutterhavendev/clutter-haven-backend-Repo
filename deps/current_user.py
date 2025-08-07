from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.user import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db)):
    # TEMP: Mock current user (simulate auth)
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user
