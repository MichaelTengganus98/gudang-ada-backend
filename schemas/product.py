from pydantic import BaseModel, HttpUrl
from typing import Optional


class ProductBase(BaseModel):
    name: str
    image_url: Optional[HttpUrl]
    description: Optional[str]


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True
