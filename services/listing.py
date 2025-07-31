from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.listing import Listing
from schemas.listing import ListingCreate


#the endpoint that lets a user create a listing.
def create_listing(data: ListingCreate, db: Session, user_id: int):
    listing = Listing(**data.model_dump(), owner_id=user_id)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


#the endpoint that returns a list of all listing created.
def get_all_listings(db: Session, skip: int = 0, limit: int = 10): #Add Pagination to Listing Search to allow the frontend to request listings in pages, improving performance and user experience.
    return db.query(Listing).offset(skip).limit(limit).all()


def get_user_listings(user_id: int, db: Session):
    return db.query(Listing).filter(Listing.owner_id == user_id).all() #Only Return Listings Belonging to the Logged-in User
#This feature supports personalized dashboards (e.g., “My Listings” view).



def search_listings(
    db: Session,
    location: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    skip: int = 0,
    limit: int = 10
):
    
    query = db.query(Listing)
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Listing.category.ilike(f"%{category}%"))
    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    return query.all()



#the endpoint that lets a user update a listing they've created.
def update_listing(listing_id: int, data: ListingCreate, db: Session, user_id: int):
    listing = db.query(Listing).filter(Listing.id == listing_id, Listing.owner_id == user_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or not authorized")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(listing, key, value)

    db.commit()
    db.refresh(listing)
    return listing



#The endpoint responsible for secure deletion of a listing, allowing only the owner to delete it.
def delete_listing(listing_id: int, db: Session, user_id: int):
    listing = db.query(Listing).filter(Listing.id == listing_id, Listing.owner_id == user_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or not authorized")

    db.delete(listing)
    db.commit()
    return {"message": "Listing deleted successfully"}






