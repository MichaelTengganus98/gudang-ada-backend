from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class CartProduct(Base):
    __tablename__ = "cart_products"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    seller_product_id = Column(Integer, ForeignKey("seller_products.id"))
    quantity = Column(Integer, default=1)
    price = Column(Integer)

    cart = relationship("Cart", back_populates="cart_products")
    seller_product = relationship("SellerProduct")
