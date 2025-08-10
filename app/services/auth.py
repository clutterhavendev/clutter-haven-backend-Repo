from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        # Use timezone-aware datetime
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        
        # Ensure sub is stored as string for consistency
        if "sub" in to_encode and isinstance(to_encode["sub"], int):
            to_encode["sub"] = str(to_encode["sub"])
            
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM],
                # Add leeway for clock skew
                leeway=timedelta(seconds=10)
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Invalid token (includes PyJWTError)
            return None
        except Exception:
            # Any other error
            return None
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None
            if not AuthService.verify_password(password, user.password_hash):
                return None
            return user
        except Exception:
            return None
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # Strip 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        payload = AuthService.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        # Get user_id from token - handle both string and int
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception
        
        try:
            # Convert to int if it's a string
            user_id = int(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
        except (ValueError, TypeError):
            raise credentials_exception
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise credentials_exception
            return user
        except Exception:
            raise credentials_exception