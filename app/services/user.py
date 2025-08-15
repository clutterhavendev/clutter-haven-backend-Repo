from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from models import User, Wallet, Vendor, VendorPlan, Role, Permission
from schemas.users import UserCreate, UserUpdate, LocationUpdate, RoleCreate, PermissionCreate
from services.auth import AuthService
from typing import List

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
    
    @staticmethod
    def update_user_location(db: Session, user_id: int, location: LocationUpdate) -> User:
        """Update user's location"""
        user = UserService.get_user_by_id(db, user_id)
        user.location = location.location
        user.location_verified = True
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def upload_id_document(db: Session, user_id: int, id_upload_url: str) -> User:
        """Upload ID document for verification"""
        try:
           user = UserService.get_user_by_id(db, user_id)
           user.id_upload_url = id_upload_url
           user.is_id_verified = True
           db.commit()
           db.refresh(user)
        except Exception as e:
           db.rollback()
           raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail="Failed to upload ID document"
           )
           return user
       
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """Create a new role and assign permissions."""
        existing_role = db.query(Role).filter(Role.name == role_data.name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists"
            )
        
        db.role = Role(
            name=role_data.name,
            description=role_data.description,
            permissions=role_data.permissions
        )
        
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_role_by_name(db: Session, role_name: str) -> Role:
        """Get role by name."""
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
    
    @staticmethod
    def create_permission(db: Session, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        existing_permission = db.query(Permission).filter(Permission.name == permission_data.name).first()
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists"
            )
        
        permission = Permission(
            name=permission_data.name,
            description=permission_data.description
        )
        
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    
    @staticmethod
    def get_permissions(db: Session) -> List[Permission]:
        """Get all permissions."""
        permissions = db.query(Permission).all()
        return permissions