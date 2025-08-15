from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.users import UserResponse, UserUpdate, LocationUpdate, PermissionResponse, RoleCreate, RoleResponse
from services.user import UserService
from services.auth import AuthService
from models import User
from typing import List

router = APIRouter()
security = HTTPBearer()

@router.get
def read_users(db: Session = Depends(get_db)):
    """Get all users"""
    return UserService.get_all_users(db)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return AuthService.get_current_user(db, credentials.credentials)

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    return UserService.update_user(db, current_user.id, user_data)

@router.put("/verify/{user_id}", response_model=UserResponse)
async def verify_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a user (self-verification for now)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this user"
        )
    
    return UserService.verify_user(db, user_id)

@router.put("/location", response_model=UserResponse)
async def update_user_location(
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's location"""
    return UserService.update_user_location(db, current_user.id, location_data)

@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    admin: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new role"""
    if not admin.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create roles"
        )
    return UserService.create_role(db, role_data)

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    admin: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions"""
    if not admin.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view permissions"
        )
    return UserService.get_permissions(db)
