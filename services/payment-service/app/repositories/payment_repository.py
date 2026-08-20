from sqlalchemy.orm import Session

from app.db.models.payment import Payment


def create_payment(
    db: Session,
    order_id: int,
    user_id: int,
    amount: float
):
    payment = Payment(
        order_id=order_id,
        user_id=user_id,
        amount=amount,
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def get_payment_by_order_id(
    db: Session,
    order_id: int
):
    return db.query(Payment).filter(
        Payment.order_id == order_id
    ).first()


def get_payment(
    db: Session,
    payment_id: int
):
    return db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


def get_user_payments(
    db: Session,
    user_id: int
):
    return db.query(Payment).filter(
        Payment.user_id == user_id
    ).all()


def get_all_payments(
    db: Session
):
    return db.query(Payment).all()


def update_payment_status(
    db: Session,
    payment: Payment,
    status: str
):
    payment.status = status

    db.commit()
    db.refresh(payment)

    return payment