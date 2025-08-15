#!/usr/bin/env python3
"""
Database initialization script for Clutter_Haven
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.session import engine, SessionLocal
from models import Base, VendorPlan, Role, Permissions
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
        
def seed_roles_and_permissions():
    """Seed initial roles and permissions"""
    print("Seeding roles and permissions...")

    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        if existing_roles > 0:
            print("✅ Roles already exist, skipping seed...")
        else:
            # Create roles
            admin_role = Role(name="admin")
            user_role = Role(name="user")
            db.add(admin_role)
            db.add(user_role)
            db.commit()
            print("✅ Roles seeded successfully!")
        return

        # Check if permissions already exist
        existing_permissions = db.query(Permissions).count()
        if existing_permissions > 0:
            print("✅ Permissions already exist, skipping seed...")
        else:
            # Create permissions
            read_permission = Permissions(name="read")
            write_permission = Permissions(name="write")
            db.add(read_permission)
            db.add(write_permission)
            db.commit()
            print("✅ Permissions seeded successfully!")

    
    # Define permissions
        perms = {
            "create_listings": "Permission to create new listings",
            "edit_own_listings": "Permission to edit own listings",
            "delete_own_listings": "Permission to delete own listings",
            "verify_user_id": "Permission to manually verify a user's ID",
            "view_permissions": "Permission to view all permissions",
            "create_roles": "Permission to create new roles",
            "delete_roles": "Permission to delete roles",
            "manage_orders": "Permission to manage orders",
            "leave_review": "Permission to leave reviews"
        }
        
        db_perms = {name: Permission(name=name, description=desc) for name, desc in perms.items()}
        db.add_all(db_perms.values())

        # Define roles with permissions
        admin_role = Role(name="admin", description="Full administrative access")
        admin_role.permissions.extend([db_perms["verify_user_id"], db_perms["view_permissions"], db_perms["create_roles"], db_perms["delete_roles"], db_perms["manage_orders"]])

        seller_role = Role(name="seller", description="Vendor user role")
        seller_role.permissions.extend([db_perms["create_listings"], db_perms["edit_own_listings"], db_perms["delete_own_listings"]])
        
        buyer_role = Role(name="buyer", description="Standard buyer user role")
        buyer_role.permissions.extend([db_perms["leave_review"]])
        
        db.add_all([admin_role, seller_role, buyer_role])
        db.commit()
        print("✅ Roles and permissions seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding roles and permissions: {e}")
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