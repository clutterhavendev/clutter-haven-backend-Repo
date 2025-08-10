from sqlalchemy.orm import Session
from app.models.vendor import VendorPlan  # Adjust import path as needed
from decimal import Decimal

class SeedService:
    @staticmethod
    def seed_vendor_plans(db: Session):
        """Seed default vendor plans if they don't exist"""
        
        # Check if plans already exist
        existing_plans = db.query(VendorPlan).count()
        if existing_plans > 0:
            print("Vendor plans already exist, skipping seed...")
            return
        
        # Define the plans based on your requirements
        plans_data = [
            {
                "name": "Basic",
                "monthly_fee": Decimal("0.00"),  # Free sign-ups
                "remittance_rate": Decimal("0.92"),  # 8% commission = 92% remittance
                "max_listings_per_month": 10,  # Limited listings
                "visibility_boost": False,
                "description": "Free sign-ups for all sellers, no subscription fee required"
            },
            {
                "name": "Premium",
                "monthly_fee": Decimal("29.99"),  # Monthly subscription
                "remittance_rate": Decimal("0.95"),  # 5% commission = 95% remittance
                "max_listings_per_month": -1,  # -1 for unlimited (or use a large number)
                "visibility_boost": True,
                "description": "Monthly subscriptions with unlimited listings and increased visibility"
            }
        ]
        
        # Create and add plans to database
        for plan_data in plans_data:
            plan = VendorPlan(**plan_data)
            db.add(plan)
        
        try:
            db.commit()
            print(f"Successfully seeded {len(plans_data)} vendor plans")
        except Exception as e:
            db.rollback()
            print(f"Error seeding vendor plans: {e}")
            raise