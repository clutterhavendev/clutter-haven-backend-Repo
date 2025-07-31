from fastapi import FastAPI
from routers import listings
from routers import reviews
app = FastAPI(
  title="Clutterhaven",
  version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ClutterHaven API"}

app.include_router(listings.router, prefix="/listings", tags=["Listings"])

app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
