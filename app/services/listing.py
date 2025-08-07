from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
import cloudinary.uploader
from datetime import datetime

from models import Listing, Vendor, VendorPlan, User
from schemas.listing import ListingCreate, ListingUpdate

#Create Listing
class ListingService:
    @staticmethod
    def create_listing(db: Session, listing_data: ListingCreate, user: User) -> Listing:
        """Create a new listing"""
        if user.user_type != "seller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only sellers can create listings"
            )
        
        vendor = db.query(Vendor).filter(Vendor.user_id == user.id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        # Check listing limits based on plan
        current_month_listings = db.query(Listing).filter(
            Listing.vendor_id == vendor.id,
            Listing.created_at >= datetime.utcnow().replace(day=1)
        ).count()
        
        vendor_plan = db.query(VendorPlan).filter(VendorPlan.id == vendor.plan_id).first()
        if current_month_listings >= vendor_plan.max_listings_per_month:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monthly listing limit reached"
            )
        
        listing = Listing(
            vendor_id=vendor.id,
            title=listing_data.title,
            description=listing_data.description,
            price=listing_data.price,
            item_condition=listing_data.item_condition,
            category=listing_data.category,
            image_url=listing_data.image_url,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(listing)
        db.commit()
        db.refresh(listing)
        return listing
    
    
    #Search listings
    @staticmethod
    def get_listings(
        db: Session,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Listing]:
        """Get listings with optional filtering"""
        query = db.query(Listing).filter(Listing.is_active == True)
        
        if category:
            query = query.filter(Listing.category == category)
        
        if search:
            query = query.filter(Listing.title.contains(search))
        
        return query.offset(skip).limit(limit).all()
    

    #Get Listing by ID
    @staticmethod
    def get_listing_by_id(db: Session, listing_id: int) -> Listing:
        """Get listing by ID"""
        listing = db.query(Listing).filter(
            Listing.id == listing_id,
            Listing.is_active == True
        ).first()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        return listing
    

    #Get listings by a user
    @staticmethod
    def get_user_listings(db: Session, user: User) -> List[Listing]:
        """Get all listings for a user"""
        if user.user_type != "seller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only sellers can view their listings"
            )
        
        vendor = db.query(Vendor).filter(Vendor.user_id == user.id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor profile not found"
            )
        
        return db.query(Listing).filter(Listing.vendor_id == vendor.id).all()
    


    #Update listing
    @staticmethod
    def update_listing(
        db: Session,
        listing_id: int,
        listing_data: ListingUpdate,
        user: User
    ) -> Listing:
        """Update a listing"""
        vendor = db.query(Vendor).filter(Vendor.user_id == user.id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendor profile not found"
            )
        
        listing = db.query(Listing).filter(
            Listing.id == listing_id,
            Listing.vendor_id == vendor.id
        ).first()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        update_data = listing_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(listing, field, value)
        
        db.commit()
        db.refresh(listing)
        return listing
    
    #Change listing status to active/inactive
    @staticmethod
    def toggle_listing_status(db: Session, listing_id: int, user: User) -> Listing:
        """Toggle listing active status"""
        vendor = db.query(Vendor).filter(Vendor.user_id == user.id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendor profile not found"
            )
        
        listing = db.query(Listing).filter(
            Listing.id == listing_id,
            Listing.vendor_id == vendor.id
        ).first()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        listing.is_active = not listing.is_active
        db.commit()
        db.refresh(listing)
        return listing
    
    #Upload Images
    @staticmethod
    def upload_image(file) -> dict:
        """Upload image to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(file.file)
            return {
                "image_url": result["secure_url"],
                "public_id": result["public_id"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image upload failed: {str(e)}"
            )