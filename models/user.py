from sqlalchemy import Column, Integer, String, Enum
from database import Base
import enum


class UserRole(str, enum.Enum):
    buyer = "buyer"
    seller = "seller"
    internal = "internal"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    address = Column(String)
    phone_number = Column(String)
    password = Column(String)
    role = Column(Enum(UserRole))
