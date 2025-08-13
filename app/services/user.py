from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
import os
import resend

from models import User, Wallet, Vendor, VendorPlan
from schemas.users import UserCreate, UserUpdate
from services.auth import AuthService

# Load Resend API key from environment variables
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY

# Secret key for email verification token
EMAIL_VERIFY_SECRET = os.getenv("EMAIL_VERIFY_SECRET", "super-secret-key")
EMAIL_VERIFY_EXPIRE_HOURS = 24  # Token expiry

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user and send verification email"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = AuthService.hash_password(user_data.password)
        db_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hashed_password,
            user_type=user_data.user_type,
            is_verified=False,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create wallet for user
        wallet = Wallet(
            user_id=db_user.id,
            balance=0.0,
            updated_at=datetime.utcnow()
        )
        db.add(wallet)
        
        # If seller, create vendor profile with basic plan
        if user_data.user_type == "seller":
            basic_plan = db.query(VendorPlan).filter(VendorPlan.name == "Basic").first()
            if not basic_plan:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Basic vendor plan not found"
                )
            
            vendor = Vendor(
                user_id=db_user.id,
                plan_id=basic_plan.id,
                verification_status="pending",
                id_verified=False,
                location_verified=False,
                created_at=datetime.utcnow()
            )
            db.add(vendor)
        
        db.commit()

        # Send verification email
        UserService.send_verification_email(db_user)

        return db_user

    @staticmethod
    def send_verification_email(user: User):
        """Send verification email via Resend"""
        token = jwt.encode(
            {
                "sub": str(user.id),
                "exp": datetime.utcnow() + timedelta(hours=EMAIL_VERIFY_EXPIRE_HOURS)
            },
            EMAIL_VERIFY_SECRET,
            algorithm="HS256"
        )

        verify_link = f"https://your-frontend-domain.com/verify-email?token={token}"

        try:
            resend.Emails.send({
                "from": "no-reply@clutterhaven.com",
                "to": user.email,
                "subject": "Verify your Clutter Haven account",
                "html": f"""
                <h1>Welcome to Clutter Haven!</h1>
                <p>Hi {user.full_name},</p>
                <p>Click the button below to verify your email:</p>
                <p><a href="{verify_link}" style="background-color:blue;color:white;padding:10px 20px;text-decoration:none;">Verify Email</a></p>
                <p>This link will expire in {EMAIL_VERIFY_EXPIRE_HOURS} hours.</p>
                """
            })
        except Exception as e:
            print(f"Error sending email: {e}")

    @staticmethod
    def verify_user(db: Session, token: str) -> User:
        """Verify a user from email token"""
        try:
            payload = jwt.decode(token, EMAIL_VERIFY_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.is_verified = True
        db.commit()
        db.refresh(user)
        return user
