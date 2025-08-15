from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime, timezone
from .base import Base


role_permission_table = Table('role_permission', Base.metadata,
        Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
        Column('permission_id', String, ForeignKey('permissions.id'), nullable=False)
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'buyer' or 'seller'
    is_verified = Column(Boolean, default=False) #phone/verification
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_admin = Column(Boolean, default=False)  # ✅ Admin capability
    role = Column(String, default="buyer")  # Default role is 'buyer'
    
    #Role and Permission Management
    role_id = Column(Integer, ForeignKey('roles.id'), nullable = False)
    role = relationship("Role", back_populates = "users")
    
    # Relationships
    vendor_profile = relationship("Vendor", back_populates="user", uselist=False)
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    orders_as_buyer = relationship("Order", back_populates="buyer")
    reviews_given = relationship("Review", back_populates="buyer")
    
    #ID and location verification
    id_upload_url = Column(String, nullable=True)
    is_id_verified = Column(Boolean, default=False)
    location_verified = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary=role_permission_table, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    
    id  = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    roles = relationship("Role", secondary=role_permission_table, back_populates="permissions")

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(DECIMAL(10, 2), default=0.00)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="wallet")