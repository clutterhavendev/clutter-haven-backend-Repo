import sys 
# import os
from pathlib import Path
import random
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
from sqlalchemy import create_engine, text, MetaData
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
        
        # Log the created vendor plans to ensure the variable is accessed
        logger.info(f"Vendor plans created: {[plan.name for plan in plans]}")
        
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