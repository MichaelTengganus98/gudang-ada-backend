from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.product import Product
from schemas.product import ProductCreate, ProductOut, ProductUpdate
from database import get_db
from auth import require_role
from models.user import UserRole
from datetime import datetime


router = APIRouter()


@router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.internal)),
):
    product_data = product.dict()
    product_data["image_url"] = str(product_data["image_url"])
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.deleted_at == None).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.internal)),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.deleted_at == None)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.internal)),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.deleted_at == None)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = update.dict(exclude_unset=True)

    # Fix HttpUrl to string
    if "image_url" in update_data:
        update_data["image_url"] = str(update_data["image_url"])

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.internal)),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.deleted_at == None)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.deleted_at = datetime.utcnow()
    db.commit()
    return {"detail": "Product deleted"}
