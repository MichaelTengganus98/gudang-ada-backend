from pydantic import BaseModel
from .seller_product import SellerProductOut
from typing import List 

class AddCartProductRequest(BaseModel):
    seller_product_id: int
    quantity: int


class UpdateCartProductRequest(BaseModel):
    quantity: int

class CartProductOut(BaseModel):
    id: int
    quantity: int
    price: float
    seller_product: SellerProductOut

    class Config:
        from_attributes = True

class CartOut(BaseModel):
    id: int
    cart_products: List[CartProductOut]

    class Config:
        from_attributes = True