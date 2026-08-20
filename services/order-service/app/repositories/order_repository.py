from sqlalchemy.orm import Session

from app.db.models.order import Order, OrderItem


def create_order(
    db: Session,
    user_id: int,
    total_amount: float,
    items: list[dict]
):
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status="pending"
    )

    db.add(order)
    db.flush()

    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            unit_price=item["unit_price"]
        )

        db.add(order_item)

    db.commit()
    db.refresh(order)

    return order


def get_order(
    db: Session,
    order_id: int
):
    return db.query(Order).filter(
        Order.id == order_id
    ).first()


def get_user_orders(
    db: Session,
    user_id: int
):
    return db.query(Order).filter(
        Order.user_id == user_id
    ).all()


def get_all_orders(
    db: Session
):
    return db.query(Order).all()



def update_order_status(
    db: Session,
    order_id: int,
    status: str
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order is None:
        return None

    order.status = status

    db.commit()
    db.refresh(order)

    return order