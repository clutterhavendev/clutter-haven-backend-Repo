from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from models import User, Wallet, Vendor, VendorPlan
from schemas.users import UserCreate, UserUpdate
from services.auth import AuthService

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
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
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Get user by email"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def verify_user(db: Session, user_id: int) -> User:
        """Verify a user"""
        user = UserService.get_user_by_id(db, user_id)
        user.is_verified = True
        db.commit()
        db.refresh(user)
        return user