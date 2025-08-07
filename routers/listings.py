from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from deps.current_user import get_current_user
from models.user import User
from db.session import SessionLocal
from schemas.listing import ListingCreate, ListingOut
from services.listing import create_listing, get_all_listings, search_listings, update_listing, get_user_listings, delete_listing
import shutil
import os
from typing import Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

MAX_FILE_SIZE_MB = 2
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

def validate_upload(file: UploadFile):
    # Validate extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Validate file size (read in chunks)
    size = 0
    for chunk in file.file:
        size += len(chunk)
        if size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
    file.file.seek(0)  # Reset pointer


#get all listings
@router.get("/", response_model=list[ListingOut])
def list_all(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return get_all_listings(db, skip=skip, limit=limit)

#search and get listing
@router.get("/search", response_model=list[ListingOut])
def search(
    location: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return search_listings(db, location, category, min_price, max_price, skip, limit)

#get listing belonging to user
@router.get("/my-listings", response_model=list[ListingOut])
def get_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    return get_user_listings(current_user.id, db) 



#Create Listing
UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=ListingOut)
def create_new_listing(
    title: str,
    description: str,
    price: float,
    location: str,
    category: str,
    condition: str,
    is_bundle: Optional[bool] = False,
    media_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    media_url = None
    if media_file:
        validate_upload(media_file)
        file_path = os.path.join(UPLOAD_DIR, media_file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(media_file.file, f)
        media_url = file_path

    data = ListingCreate(
        title=title,
        description=description,
        price=price,
        location=location,
        category=category,
        condition=condition,
        is_bundle=is_bundle,
        media_url=media_url
    )

    return create_listing(data, db, current_user.id)

#Update
@router.put("/{listing_id}", response_model=ListingOut)
def update_listing_route(
    listing_id: int,
    listing_data: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_listing(listing_id, listing_data, db, current_user.id)


#Delete
@router.delete("/{listing_id}")
def delete_listing_route(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_listing(listing_id, db, current_user.id)


# Admin suspend or unsuspend a listing
@router.patch("/admin/{listing_id}/toggle-active")
def toggle_listing_active_status(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")

    listing = db.query(listing).filter(listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing.is_active = not listing.is_active
    db.commit()
    return {"message": f"Listing {'reactivated' if listing.is_active else 'suspended'} successfully."}
