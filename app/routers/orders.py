from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import Order, User, Admin, Product, OrderItem
from app.dependencies.auth import get_current_user, get_current_admin
from app.routers.schemas import OrderCreate, OrderRead, OrderItemCreate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderRead, status_code=201)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_order = Order(
        user_id=current_user.user_id,
        total_amount=order.total_amount,
        status=order.status,
        sale_source=order.sale_source
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Add order items
    for item in order.order_items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {item.product_id}")

        order_item = OrderItem(
            order_id=new_order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase
        )

        product.stock -= item.quantity  # Reduce stock
        db.add(order_item)

    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/{order_id}", response_model=OrderRead)
def read_order(
        order_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    order = session.exec(
        select(Order).where(Order.order_id == order_id)
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")

    return order


@router.get("/", response_model=List[OrderRead])
def read_orders(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    orders = session.exec(select(Order).where(Order.user_id == current_user.user_id)).all()

    return orders


@router.put("/{order_id}/items", status_code=200)
def update_order_items(
    order_id: int,
    order_items: List[OrderItemCreate],
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this order")

    # Delete existing order items
    db.exec(select(OrderItem).where(OrderItem.order_id == order_id)).delete()

    for item in order_items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {item.product_id}")

        order_item = OrderItem(
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase
        )

        product.stock -= item.quantity
        db.add(order_item)

    db.commit()
    return {"message": "Order items updated"}
