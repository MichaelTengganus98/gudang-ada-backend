from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session, joinedload
from models import (
    User,
    UserRole,
    SellerProduct,
    Cart,
    CartProduct,
    Order,
    OrderStatus,
    OrderProduct,
    Product,
)
from schemas.order import OrderOut, OrderStatusUpdate
from database import get_db
from auth import get_current_user, require_role
from typing import List, Optional

router = APIRouter()


@router.post("/checkout")
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.buyer)),
):
    cart = (
        db.query(Cart)
        .options(joinedload(Cart.cart_products).joinedload(CartProduct.seller_product))
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart or not cart.cart_products:
        raise HTTPException(status_code=400, detail="Cart is empty.")

    seller_group = {}
    for item in cart.cart_products:
        seller_id = item.seller_product.seller_id
        seller_group.setdefault(seller_id, []).append(item)

    for seller_id, products in seller_group.items():
        # ✅ Changed user_id to buyer_id
        order = Order(buyer_id=current_user.id, seller_id=seller_id)
        db.add(order)
        db.flush()

        for product in products:
            order_product = OrderProduct(
                order_id=order.id,
                seller_product_id=product.seller_product_id,
                quantity=product.quantity,
                price=product.price,
            )
            db.add(order_product)

    db.query(CartProduct).filter(CartProduct.cart_id == cart.id).delete()
    db.query(Cart).filter(Cart.id == cart.id).delete()

    db.commit()
    return {"message": "Checkout successful"}

@router.get("", response_model=List[OrderOut])
def get_orders(
    buyer_id: Optional[str] = Query(None),
    seller_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Order).options(
        joinedload(Order.order_products)
        .joinedload(OrderProduct.seller_product)
        .joinedload(SellerProduct.product)
    )

    if buyer_id and buyer_id.isdigit():
        query = query.filter(Order.buyer_id == int(buyer_id))

    if seller_id and seller_id.isdigit():
        query = query.filter(Order.seller_id == int(seller_id))

    return query.all()


@router.patch("/{order_id}")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.seller)),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.seller_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this order"
        )

    if order.status in [OrderStatus.REJECTED, OrderStatus.COMPLETED]:
        raise HTTPException(
            status_code=400, detail="Cannot update a completed or rejected order"
        )

    if status_update.status not in [
        OrderStatus.CONFIRMED,
        OrderStatus.REJECTED,
        OrderStatus.COMPLETED,
    ]:
        raise HTTPException(status_code=400, detail="Invalid status transition")

    order.status = status_update.status
    db.commit()
    db.refresh(order)

    return {"message": f"Order status updated to {order.status}"}
