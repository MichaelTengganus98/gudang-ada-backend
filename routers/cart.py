from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from auth import require_role
from models.seller_product import SellerProduct
from models.user import UserRole, User
from models.cart_product import CartProduct
from models.cart import Cart
from schemas.cart_product import (
    AddCartProductRequest,
    UpdateCartProductRequest,
    CartOut,
)

router = APIRouter()


@router.get("/count")
def get_cart_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.buyer)),
):
    total_items = (
        db.query(CartProduct).join(Cart).filter(Cart.user_id == current_user.id).count()
    )
    return {"count": total_items}


@router.get("/", response_model=CartOut)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.buyer)),
):
    cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.cart_products)
            .joinedload(CartProduct.seller_product)
            .joinedload(SellerProduct.product)
        )
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    return cart


@router.post("/")
def add_to_cart(
    req: AddCartProductRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.buyer)),
):
    seller_product = (
        db.query(SellerProduct)
        .options(joinedload(SellerProduct.product))
        .filter(SellerProduct.id == req.seller_product_id)
        .first()
    )
    if not seller_product:
        raise HTTPException(status_code=404, detail="SellerProduct not found")

    product = seller_product.product

    cart = db.query(Cart).filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_product = (
        db.query(CartProduct)
        .filter_by(cart_id=cart.id, seller_product_id=req.seller_product_id)
        .first()
    )
    if cart_product:
        cart_product.quantity += req.quantity
    else:
        cart_product = CartProduct(
            cart_id=cart.id,
            seller_product_id=req.seller_product_id,
            quantity=req.quantity,
            price=seller_product.price,
        )
        db.add(cart_product)

    db.commit()
    return {"message": "Product added to cart"}


@router.delete("/{cart_product_id}")
def delete_cart_product(
    cart_product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.buyer)),
):
    cart_product = db.query(CartProduct).get(cart_product_id)
    if not cart_product:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_product)
    db.commit()
    return {"message": "Cart product deleted"}


@router.put("/{cart_product_id}")
def update_cart_quantity(
    cart_product_id: int,
    req: UpdateCartProductRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.buyer)),
):
    cart_product = db.query(CartProduct).get(cart_product_id)
    if not cart_product:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_product.quantity = req.quantity
    db.commit()
    return {"message": "Quantity updated"}
