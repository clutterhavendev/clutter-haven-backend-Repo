from pydantic import BaseModel

class WalletOut(BaseModel):
    user_id: int
    balance: float

    class Config:
        orm_mode = True