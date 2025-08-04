from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    buyer = "buyer"
    seller = "seller"
    internal = "internal"

class UserCreate(BaseModel):
    user_id: str
    name: str
    address: str
    phone_number: str
    password: str
    role: UserRole

class UserOut(BaseModel):
    id: int
    user_id: str
    name: str
    address: str
    phone_number: str
    role: UserRole

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    user_id: str
    password: str