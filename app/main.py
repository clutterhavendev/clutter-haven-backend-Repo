import sys
import os

# Adding the root and app directories to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)
sys.path.insert(0, app_dir)

from .routers import auth, user, vendor, listings, orders, wallets, reviews

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cloudinary

from .routers import auth, user, vendor, listings, orders, wallets, reviews
from db.session import engine, SessionLocal  # Added SessionLocal import
from models.base import Base
from config import settings
from .services.seed_service import SeedService  # Added SeedService import

# Initialize Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="ClutterHaven",
    description="Create Space for What Matters",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event for database seeding
@app.on_event("startup")
async def startup_event():
    """Run startup tasks including database seeding"""
    db = SessionLocal()
    try:
        # Seed vendor plans
        SeedService.seed_vendor_plans(db)
        print("Database seeding completed")
    except Exception as e:
        print(f"Database seeding failed: {e}")
    finally:
        db.close()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(vendor.router, prefix="/vendors", tags=["Vendors"])
app.include_router(listings.router, prefix="/listings", tags=["Listings"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to ClutterHaven API",
    
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )