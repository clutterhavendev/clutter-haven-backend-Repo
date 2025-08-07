from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db import Base



reviews = relationship("Review", back_populates="user", cascade="all, delete")

is_admin = Column(Boolean, default=False)

listings = relationship("Listing", back_populates="owner")