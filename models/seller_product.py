from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class SellerProduct(Base):
    __tablename__ = "seller_products"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Integer, default=0)

    deleted_at = Column(DateTime, nullable=True)

    seller = relationship("User", back_populates="seller_products")
    product = relationship("Product", back_populates="seller_products")
