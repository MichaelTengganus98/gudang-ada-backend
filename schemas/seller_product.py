from pydantic import BaseModel
from schemas.product import ProductOut



class SellerProductBase(BaseModel):
    product_id: int
    quantity: int
    price: int



class SellerProductOut(SellerProductBase):
    id: int
    seller_id: int
    product: ProductOut

    class Config:
        from_attributes = True


class SellerProductUpdate(SellerProductBase):
    pass
