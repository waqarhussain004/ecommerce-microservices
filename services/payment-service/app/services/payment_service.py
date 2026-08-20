from sqlalchemy.orm import Session

from app.repositories.payment_repository import (
     create_payment,
    get_payment,
    get_payment_by_order_id,
    get_user_payments,
    get_all_payments,
    update_payment_status
)
from app.services.order_client import (
    get_order,
    confirm_order
)
from app.core.settings import SERVICE_SECRET
from app.schemas.payment import PaymentStatus



def create_payment_service(
    db: Session,
    order_id: int,
    user_id: int,
    token: str
):

    order = get_order(
        order_id=order_id,
        token=token
    )

    if order is None:
        raise ValueError("Order not found")

   
    if order["user_id"] != user_id:
        raise PermissionError(
            "You are not allowed to pay for this order"
        )

   
    if order["status"] != "pending":
        raise ValueError(
            f"Order cannot be paid from "
            f"{order['status']} status"
        )

    
    existing_payment = get_payment_by_order_id(
        db=db,
        order_id=order_id
    )

    if existing_payment is not None:
        raise ValueError(
            "Payment already exists for this order"
        )

    
    amount = order["total_amount"]

    
    payment = create_payment(
        db=db,
        order_id=order_id,
        user_id=user_id,
        amount=amount
    )

    
    payment = update_payment_status(
        db=db,
        payment=payment,
        status=PaymentStatus.SUCCESSFUL.value
    )

    
    confirmed_order = confirm_order(
        order_id=order_id,
        service_secret=SERVICE_SECRET
    )

    if confirmed_order is None:
        raise ValueError("Order not found")

    return payment



def process_payment_service(
    db: Session,
    payment_id: int,
    user_id: int
):
    payment = get_payment(
        db=db,
        payment_id=payment_id
    )

    if payment is None:
        raise ValueError("Payment not found")

    if payment.user_id != user_id:
        raise PermissionError(
            "You are not allowed to process this payment"
        )

    if payment.status != "pending":
        raise ValueError(
            f"Payment cannot be processed from "
            f"{payment.status} status"
        )

    payment = update_payment_status(
        db=db,
        payment=payment,
        status="successful"
    )

    return payment


def get_payment_service(
    db: Session,
    payment_id: int,
    current_user: dict
):
    payment = get_payment(
        db=db,
        payment_id=payment_id
    )

    if payment is None:
        raise ValueError("Payment not found")

    if current_user["role"] == "admin":
        return payment

    if payment.user_id != current_user["id"]:
        raise PermissionError(
            "You are not allowed to view this payment"
        )

    return payment



def get_my_payments_service(
    db: Session,
    current_user: dict
):
    # Admin → all payments
    if current_user["role"] == "admin":
        return get_all_payments(db)

    # User → own payments
    return get_user_payments(
        db=db,
        user_id=current_user["id"]
    )