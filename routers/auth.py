from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, db

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_dependency = Depends(db.get_db)

@router.post("/register", response_model= schemas.users)
def register(user: schemas.UserCreate, db: Session = db_dependency):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = db_dependency):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}
