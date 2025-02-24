from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import Payment, Order, User
from app.dependencies.auth import get_current_user
from app.routers.schemas import PaymentCreate, PaymentRead
from typing import List

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentRead, status_code=201)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    order = db.get(Order, payment.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this order")

    if payment.amount > order.total_amount:
        raise HTTPException(status_code=400, detail="Payment amount exceeds order total")

    new_payment = Payment(
        order_id=payment.order_id,
        payment_method=payment.payment_method,
        amount=payment.amount,
        status="completed"  # Assume payment is completed for now
    )

    # Update order status if fully paid
    total_paid = sum(p.amount for p in db.exec(select(Payment).where(Payment.order_id == payment.order_id)))
    if total_paid + payment.amount >= order.total_amount:
        order.status = "paid"

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


@router.get("/", response_model=List[PaymentRead])
def get_payments(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    payments = db.exec(
        select(Payment).join(Order).where(Order.user_id == current_user.user_id)
    ).all()

    return payments


@router.put("/{payment_id}/status", response_model=PaymentRead)
def update_payment_status(
        payment_id: int,
        status: str,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    order = db.get(Order, payment.order_id)
    if order.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this payment")

    if status not in ["pending", "completed", "failed", "refunded"]:
        raise HTTPException(status_code=400, detail="Invalid payment status")

    payment.status = status
    db.commit()
    db.refresh(payment)

    return payment

