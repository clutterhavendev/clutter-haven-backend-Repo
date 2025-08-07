#!/usr/bin/env python3
"""
Database initialization script for Clutter_Haven
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.session import engine, SessionLocal
from models import Base, VendorPlan
from config import settings

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

def seed_vendor_plans():
    """Seed initial vendor plans"""
    print("Seeding vendor plans...")
    
    db = SessionLocal()
    try:
        # Check if plans already exist
        existing_plans = db.query(VendorPlan).count()
        if existing_plans > 0:
            print("✅ Vendor plans already exist, skipping seed...")
            return
        
        # Create basic plan
        basic_plan = VendorPlan(
            name="basic",
            monthly_fee=0.00,
            remittance_rate=85.00,  # 85% to seller, 15% platform fee
            max_listings_per_month=10,
            visibility_boost=False
        )
        
        # Create premium plan
        premium_plan = VendorPlan(
            name="premium",
            monthly_fee=29.99,
            remittance_rate=92.00,  # 92% to seller, 8% platform fee
            max_listings_per_month=100,
            visibility_boost=True
        )
        
        db.add(basic_plan)
        db.add(premium_plan)
        db.commit()
        print("✅ Vendor plans seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding vendor plans: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """Initialize the complete database"""
    print("🚀 Initializing PreLoved Marketplace Database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        create_tables()
        seed_vendor_plans()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Update your .env file with proper database credentials")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the API: uvicorn main:app --reload")
        print("4. Visit http://localhost:8000/docs for API documentation")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_database()