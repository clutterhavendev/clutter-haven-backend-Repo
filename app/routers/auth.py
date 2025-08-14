from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.users import UserCreate, UserLogin, UserResponse
from services.user import UserService
from services.auth import AuthService
import resend
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

resend.api_key = os.getenv("RESEND_API_KEY")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and send verification email."""
    
    # Check if API key is loaded
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        logger.error("RESEND_API_KEY environment variable not found")
        raise HTTPException(status_code=500, detail="Email service configuration error")
    
    logger.info(f"Using API key: {api_key[:10]}..." if api_key else "No API key")
    
    user = UserService.create_user(db, user_data)

    # Create JWT verification token
    token = AuthService.create_access_token(
        data={"user_id": user.id, "email": user.email}
    )

    verification_link = f"https://yourdomain.com/verify-email?token={token}"
    
    # Send verification email
    try:
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": user.email,
            "subject": "Verify your email - Clutter Haven",
            "html": f"""
                <h2>Welcome to Clutter Haven!</h2>
                <p>Click the link below to verify your email address:</p>
                <a href="{verification_link}">Verify Email</a>
                <p>This link will expire in 24 hours.</p>
            """
        })
        logger.info(f"Email sent successfully: {response}")
        
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"User email: {user.email}")
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

    return user


@router.get("/test-email")
async def test_email():
    """Test email sending configuration."""
    try:
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            return {"error": "No API key found", "has_key": False}
        
        # Check if key format is correct
        if not api_key.startswith("re_"):
            return {"error": "Invalid API key format", "key_prefix": api_key[:5] if len(api_key) > 5 else api_key}
            
        logger.info(f"Testing email with API key: {api_key[:10]}...")
        
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": "test@example.com",  # Replace with a real email for testing
            "subject": "Test Email from Clutter Haven",
            "html": "<p>This is a test email from your Clutter Haven backend</p>"
        })
        return {"success": True, "response": response, "has_key": True}
        
    except Exception as e:
        logger.error(f"Test email failed: {str(e)}")
        return {
            "error": str(e), 
            "type": type(e).__name__,
            "has_key": bool(os.getenv("RESEND_API_KEY")),
            "key_prefix": os.getenv("RESEND_API_KEY")[:5] if os.getenv("RESEND_API_KEY") else None
        }


@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    """Verify email using the JWT token."""
    
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = UserService.get_user_by_id(db, payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mark user as verified
    user.is_verified = True
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