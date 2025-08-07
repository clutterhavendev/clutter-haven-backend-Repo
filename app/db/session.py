from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings


# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


