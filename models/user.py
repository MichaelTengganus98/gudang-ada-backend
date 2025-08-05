<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, Enum
from database import Base
=======
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from .base import Base
>>>>>>> db2901f... implement cart
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
<<<<<<< HEAD
=======

    deleted_at = Column(DateTime, nullable=True)

    seller_products = relationship("SellerProduct", back_populates="seller")
    cart = relationship("Cart", back_populates="user", uselist=False)
>>>>>>> db2901f... implement cart
