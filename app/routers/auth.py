from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.users import UserCreate, UserLogin, UserResponse
from services.user import UserService
from services.auth import AuthService
import resend
import uuid
import os

router = APIRouter()

resend.api_key = os.getenv("RESEND_API_KEY")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and send verification email."""
 
    user = UserService.create_user(db, user_data)

    token = str(uuid.uuid4())
    UserService.save_verification_token(db, user.id, token)

    verification_link = f"https://yourdomain.com/verify-email?token={token}"

    try:
        resend.Emails.send({
            "from": "no-reply@clutterhaven.com",
            "to": user.email,
            "subject": "Verify your email - Clutter Haven",
            "html": f"""
                <h2>Welcome to Clutter Haven!</h2>
                <p>Click the link below to verify your email address:</p>
                <a href="{verification_link}">Verify Email</a>
                <p>This link will expire in 24 hours.</p>
            """
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

    return user


@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
   
    user = UserService.get_user_by_verification_token(db, token)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    # Mark user as verified
    user.is_verified = True
    user.verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in."
        )

    access_token = AuthService.create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
