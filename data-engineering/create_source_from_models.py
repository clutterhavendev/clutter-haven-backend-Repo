import sys 
# import os
from pathlib import Path
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import pandas as pd
from sqlalchemy import create_engine, text, MetaData
from typing import List
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv
from config import source_prototype_engine
import bcrypt
import logging

# Add paths
parent_path = Path(__file__).parent.parent
app_path = parent_path / "app"
sys.path.insert(0, str(parent_path))
sys.path.insert(0, str(app_path))

from app.models.base import Base
from app.models.user import User, Wallet
from app.models.vendor import Vendor, VendorPlan
from app.models.listing import Listing 
from app.models.order import Order, Payment, DeliveryRequest
from app.models.reviews import Review 

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("create_source_from_models.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# initialize Faker
fake = Faker()

# Establish Session
SessionLocal = sessionmaker(bind=source_prototype_engine)

def create_database_from_models():
    """Create all tables from the SQLAlchemy models"""
    logger.info("Starting database schema creation")
    
    try:
        Base.metadata.drop_all(bind=source_prototype_engine)
        logger.info("Dropped existing tables")
        
        Base.metadata.create_all(bind=source_prototype_engine)
        logger.info("Created database schema from models")
        
    except Exception as e:
        logger.error(f"Failed to create database schema: {e}")
        raise 
    
def hash_password(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_vendor_plans(session: Session):
    """Create vendor plans"""
    logger.info("Creating vendor plans")
    
    plans = [
        VendorPlan(
            name='basic',
            monthly_fee=0.00,
            remittance_rate=15.00, # 15% commission
            max_listings_per_month=20,
            visibility_boost=False,
            description="Perfect for all small vendors starting out"
        ),
        VendorPlan(
            name='premium',
            monthly_fee=5000.00,  # ₦5000/month
            remittance_rate=10.00,  # 10% commission
            max_listings_per_month=100,
            visibility_boost=True,
            description="Best for established vendors with high volume"            
        )
    ]
    
    session.bulk_save_objects(plans)
    session.commit()
    logger.info("Created 2 vendor plans")
    
    return session.query(VendorPlan).all()

def generate_users(session: Session, n: int = 1000):
    """Generate user date"""
    logger.info(f"Generating {n} users...")
    
    nigerian_cities = ['Lagos', 'Abuja', 'Kano', 'Ibadan', 'Port Harcourt', 
                      'Benin City', 'Kaduna', 'Enugu', 'Aba', 'Onitsha']
    
    users = []
    for i in range(n):
        created_date = fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.utc)
        
        # 20% sellers, 80% buyers
        user_type = 'seller' if random.random() < 0.2 else 'buyer'
        
        user = User(
            full_name=fake.name(),
            email=f"user{i+1}@clutterhaven.com",
            phone=f"+234{random.randint(7000000000, 9099999999)}",
            password_hash=hash_password("password123"),  # In real app, each would be different
            user_type=user_type,
            is_verified=random.choice([True, True, True, False]),  # 75% verified
            created_at=created_date,
            is_admin=(i == 0)  # First user is admin
        )
        
        session.add(user)
        
    session.commit()
    logger.info(f"Generated {n} users")
    
    # Create wallets for all users
    users = session.query(User).all()
    for user in users:
        wallet = Wallet(
            user_id=user.id,
            balance=random.uniform(0, 50000),  # Random balance up to ₦50,000
            updated_at=user.created_at
        )
        session.add(wallet)
        
    session.commit()
    logger.info("Created wallets for all users")
    
    return users

def generate_vendors(session: Session, users: List[User], plans: List[VendorPlan]):
    """Generate vendor data for seller users"""
    seller_users = [u for u in users if getattr(u, 'user_type', None) == 'seller']
    logger.info(f"Generating vendors for {len(seller_users)} seller ")
    
    vendors: List[Vendor] = []
    for user in seller_users:
        # 70% basic plan, 30% premium
        plan = plans[0] if random.random() < 0.7 else plans[1]
        
        vendor = Vendor(
            user_id=user.id,
            plan_id=plan.id,
            verification_status=random.choice(['verified', 'verified', 'verified', 'pending', 'rejected']),
            id_verified=random.choice([True, True, False]),
            location_verified=random.choice([True, True, False]),
            created_at=user.created_at + timedelta(days=random.randint(1, 30))            
        )
        vendors.append(vendor)
        session.add(vendor)
        
    session.commit()
    logger.info(f"Created {len(vendors)} vendors")
    
    return session.query(Vendor).all()

def populate_database():
    """Main function to populate the database"""
    logger.info("Starting database population process....")
    
    # Create schema
    create_database_from_models()
    
    # Create session
    session = SessionLocal()
    
    try:
        # Create vendor plans first
        plans = create_vendor_plans(session)
        logger.info(f"Vendor plans created: {[plan.name for plan in plans]}")
        
        # Generate users and wallets
        users = generate_users(session, 10)
        logger.info(f"Generated {len(users)} users")
        
        # Generate vendors
        vendors = generate_vendors(session, users, plans)
        logger.info(f"Generated {len(vendors)} vendors")
        
        logger.info("\nDatabase population completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during database population: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        
if __name__ == "__main__":
    response = input("This will create/recreate the test database. Continue? (yes/no): ")
    if response.lower() == 'yes':
        populate_database()
    else:
        logger.info("Operation cancelled by user.")