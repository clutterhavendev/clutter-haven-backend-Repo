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

def generate_listings(session: Session, vendors: List[Vendor], n: int = 1000):
    """Generate listing"""
    logger.info(f"Generating {n} listings...")
    
    categories = {
        'Electronics': ['Phone', 'Laptop', 'Tablet', 'Headphones', 'Camera', 'TV', 'Gaming Console'],
        'Fashion': ['Shirt', 'Dress', 'Shoes', 'Bag', 'Watch', 'Jewelry', 'Sunglasses'],
        'Home & Garden': ['Furniture', 'Decor', 'Kitchen Appliance', 'Garden Tools', 'Lighting'],
        'Books': ['Fiction', 'Non-fiction', 'Educational', 'Comics', 'Magazines'],
        'Sports': ['Equipment', 'Apparel', 'Shoes', 'Accessories', 'Fitness Gear'],
        'Beauty': ['Skincare', 'Makeup', 'Hair Care', 'Perfume', 'Tools'],
        'Toys': ['Action Figures', 'Board Games', 'Puzzles', 'Dolls', 'Educational'],
        'Vehicles': ['Car Parts', 'Motorcycle Parts', 'Accessories', 'Tools']
    }
   
    conditions = ['new', 'like new', 'good', 'fair']

    # Only verified vendors can create listings
    active_vendors = [v for v in vendors if getattr(v, 'verification_status', None) == 'verified']
    
    listings: List[Listing] = []
    for i in range(n):
        vendor = random.choice(active_vendors)
        category = random.choice(list(categories.keys()))
        item_type = random.choice(categories[category])
        
        listing = Listing(
            vendor_id=vendor.id,
            title=f"{fake.company()} {item_type}",
            description=fake.text(max_nb_chars=500),
            price=round(random.uniform(500, 100000), 2),  # ₦500 to ₦100,000
            item_condition=random.choice(conditions),
            category=category,
            image_url=f"https://example.com/images/listing_{i+1}.jpg",
            is_active=random.choice([True, True, True, False]),  # 75% active
            created_at=vendor.created_at + timedelta(days=random.randint(1, 180))
        )
        listings.append(listing)
        session.add(listing)
        
    session.commit()
    logger.info(f"Created {n} listings")
    
    return session.query(Listing).all()

def generate_orders(session: Session, users: List[User], listings: List[Listing], n: int = 1000):
    """Generate orders"""
    logger.info(f"Generating {n} orders...")
    
    # Only buyers make orders
    buyers = [u for u in users if getattr(u, 'user_type', None) == 'buyer']
    # Only active listings can be ordered
    active_listings = [l for l in listings if getattr(l, 'is_active', None) == True]
    
    orders: List[Order] = []
    for _ in range(n):
        buyer = random.choice(buyers)
        listing = random.choice(active_listings)
        
        # Ensure listing.created_at is a datetime, not a Column object
        listing_created_at = getattr(listing, 'created_at', None)
        if not isinstance(listing_created_at, datetime):
            raise ValueError("listing.created_at is not a datetime object")
        
        # Order date is after listing creation
        order_date = fake.date_time_between(
            start_date=listing_created_at,
            end_date='now',
            tzinfo=timezone.utc
        )
        
        # Status progression with dates
        status = random.choices(
            ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'],
            weights=[0.1, 0.15, 0.25, 0.5, 0.1]
        )[0]
        
        delivered_at = None
        if status == 'delivered':
            delivered_at = order_date + timedelta(days=random.randint(3, 10))
                
        order = Order(
            buyer_id=buyer.id,
            listing_id=listing.id,
            status=status,
            ordered_at=order_date,
            delivered_at=delivered_at
        )
        session.add(order)
        orders.append(order)
    
    session.commit()
    logger.info(f"Created {n} orders")
    
    return session.query(Order).all()

def generate_payments(session: Session, orders: List[Order]):
    """Generate payments for orders"""
    logger.info(f"Generating payments.....")
    
    payments: List[Payment] = []
    for order in orders:
        # All orders except pending have payments
        if getattr(order, 'status', None) != 'pending':
            listing = session.query(Listing).filter_by(id=order.listing_id).first()
            
            if listing is not None and hasattr(listing, 'price'):
                price_value = getattr(listing, 'price', None)
                if price_value is not None and not hasattr(price_value, 'expression'):  
                    payment = Payment(
                        order_id=order.id,
                        amount=price_value,
                        payment_method=random.choice(['card', 'wallet']),
                        status='completed' if getattr(order, 'status', None) != 'pending' else 'pending',
                        created_at=order.ordered_at + timedelta(minutes=random.randint(1, 30))
                    )
                    payments.append(payment)
                    session.add(payment)
                else:
                    logger.warning(f"Listing price is not a valid value for order_id={order.id}")
            else:
                logger.warning(f"Listing not found or missing price for order_id={order.id}")
    
    session.commit()
    logger.info(f"Created {len(payments)} payments")
    
    return payments

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
        
        # Generate listings
        listings = generate_listings(session, vendors, 100)
        logger.info(f"Generated {len(listings)} listings")
        
        # Generate orders
        orders = generate_orders(session, users, listings, 10)
        logger.info(f"Generated {len(orders)} orders")
        
        # Generate payments
        payments = generate_payments(session, orders)
        logger.info(f"Generated {len(payments)} payments")
        
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