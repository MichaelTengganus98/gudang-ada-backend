from pydantic import BaseModel
from .seller_product import SellerProductOut
from .user import UserOut
from models import OrderStatus
from typing import List

class OrderProductOut(BaseModel):
    id: int
    order_id: int
    seller_product_id: int
    quantity: int
    price: int
    seller_product: SellerProductOut

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    buyer: UserOut
    seller: UserOut
    order_products: List[OrderProductOut]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus