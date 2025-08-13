from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int
    email: str

# 🔹 For email verification
class EmailVerificationRequest(BaseModel):
    token: str  # Token from the verification link

class EmailVerificationResponse(BaseModel):
    message: str
    email: EmailStr
    is_verified: bool
