from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image_url = Column(String)
    description = Column(String)
    deleted_at = Column(DateTime, nullable=True)

    seller_products = relationship("SellerProduct", back_populates="product")
