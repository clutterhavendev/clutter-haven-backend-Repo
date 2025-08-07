from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
import cloudinary
import cloudinary.uploader





class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://clutterhaven:1234@localhost:5432/Clutter_Haven"
    

# JWT
    SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24


# Cloudinary
    CLOUDINARY_CLOUD_NAME: str = "dnauc5t08"

    CLOUDINARY_API_KEY: str = "531375577919433"
    CLOUDINARY_API_SECRET: str = "FZq4-vnEyVNF9io1NJv3shTUm2E"

# API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "*"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()