from fastapi import APIRouter, Query, Path, Depends, Query
from sqlalchemy.orm import Session
from models.seller_product import SellerProduct
from models.user import User
from models.product import Product
from database import get_db

router = APIRouter()


@router.get("/")
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
            "seller_product_id": sp.id,
            "product_id": sp.product.id,
            "product_name": sp.product.name,
            "quantity": sp.quantity,
            "price": sp.price,
        }
        for sp in results
    ]