from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import Order, User, Admin
from app.dependencies.auth import get_current_user, get_current_admin
from app.routers.schemas import OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderRead, status_code=201)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_order = Order(**order.dict(), user_id=current_user.user_id)  # No from_orm()
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/{order_id}", response_model=OrderRead)
def read_order(
        order_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Ensure the order belongs to the current user
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
