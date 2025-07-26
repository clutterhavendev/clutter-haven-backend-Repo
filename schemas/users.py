from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

    class ShowUser(UserBase):
        id: int
        is_seller: bool
        
        class Config:
            orm_mode = True