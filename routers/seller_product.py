from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.seller_product import SellerProduct
from models.product import Product
from schemas.seller_product import (
    SellerProductBase,
    SellerProductOut,
    SellerProductUpdate,
)
from auth import get_current_user, require_role
from models.user import UserRole, User

router = APIRouter()


@router.get("/seller-products/browse")
def browse_products(
    query: str = Query(None),
    seller_id: int = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(SellerProduct).join(SellerProduct.product).join(SellerProduct.seller)

    if query:
        q = q.filter(
            (Product.name.ilike(f"%{query}%")) | (User.name.ilike(f"%{query}%"))
        )

    if seller_id:
        q = q.filter(SellerProduct.seller_id == seller_id)

    results = q.all()

    return [
        {
            "seller_id": sp.seller.id,
            "seller_name": sp.seller.name,
            "product_id": sp.product.id,
            "product_name": sp.product.name,
            "quantity": sp.quantity,
            "price": sp.price,
        }
        for sp in results
    ]


@router.post("", response_model=SellerProductOut)
def create_seller_product(
    item: SellerProductBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.seller)),
):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = (
        db.query(SellerProduct)
        .filter(
            SellerProduct.seller_id == current_user.id,
            SellerProduct.product_id == item.product_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Product already listed")

    seller_product = SellerProduct(
        seller_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity,
        price=item.price,
    )
    db.add(seller_product)
    db.commit()
    db.refresh(seller_product)
    return seller_product


@router.get("/{user_id}", response_model=list[SellerProductOut])
def get_seller_products(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(SellerProduct)
        .filter(SellerProduct.seller_id == user_id, SellerProduct.deleted_at == None)
        .all()
    )


@router.put("/{id}", response_model=SellerProductOut)
def update_seller_product(
    id: int,
    item: SellerProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.seller)),
):
    seller_product = (
        db.query(SellerProduct)
        .filter(
            SellerProduct.id == id,
            SellerProduct.seller_id == current_user.id,
            SellerProduct.deleted_at == None,
        )
        .first()
    )
    if not seller_product:
        raise HTTPException(status_code=404, detail="Seller product not found")

    seller_product.quantity = item.quantity
    seller_product.price = item.price
    db.commit()
    db.refresh(seller_product)
    return seller_product


@router.delete("/{id}")
def delete_seller_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.seller)),
):
    seller_product = (
        db.query(SellerProduct)
        .filter(
            SellerProduct.id == id,
            SellerProduct.seller_id == current_user.id,
            SellerProduct.deleted_at == None,
        )
        .first()
    )
    if not seller_product:
        raise HTTPException(status_code=404, detail="Seller product not found")

    seller_product.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Seller product deleted"}
