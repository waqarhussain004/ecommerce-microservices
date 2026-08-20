from sqlalchemy.orm import Session
from app.schemas.order import OrderStatus
from app.repositories.order_repository import (
    create_order,
    get_user_orders,
    get_all_orders,
    get_order,
    update_order_status
)

from app.services.product_client import (
    get_product,
    update_product_stock,
    restore_product_stock
)



def create_order_service(
    db: Session,
    user_id: int,
    items: list,
    token: str
):
    order_items = []
    total_amount = 0

    for item in items:

        product = get_product(
            item.product_id,
            token
        )


        if product is None:
            raise ValueError(
                f"Product {item.product_id} not found"
            )

        # Stock check
        if product["stock"] < item.quantity:
            raise ValueError(
                f"Insufficient stock for product "
                f"{item.product_id}. "
                f"Available stock: {product['stock']}"
            )

        # Product Service actual price
        unit_price = product["price"]

        # Item total
        item_total = unit_price * item.quantity

        total_amount += item_total

        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": unit_price
        })


    reduced_items = []

    try:

        for item in order_items:

            updated_product = update_product_stock(
                product_id=item["product_id"],
                quantity=item["quantity"],
                token=token
            )

            # Product not found
            if updated_product is None:
                raise ValueError(
                    f"Product {item['product_id']} not found"
                )

            # Successfully reduced
            reduced_items.append(item)

    except Exception as e:


        for item in reduced_items:

            try:
                pass

            except Exception:
                pass

        raise ValueError(
            f"Stock update failed: {str(e)}"
        )



    order = create_order(
        db=db,
        user_id=user_id,
        total_amount=total_amount,
        items=order_items
    )

    return order




def get_my_orders_service(
    db: Session,
    current_user: dict
):
    if current_user["role"] == "admin":
        return get_all_orders(db)

    return get_user_orders(
        db=db,
        user_id=current_user["id"]
    )



def get_order_service(
    db: Session,
    order_id: int,
    current_user: dict
):
    order = get_order(
        db=db,
        order_id=order_id
    )

    if order is None:
        raise ValueError("Order not found")

    if current_user["role"] == "admin":
        return order

    
    if order.user_id != current_user["id"]:
        raise PermissionError(
            "You are not allowed to view this order"
        )

    return order


def update_order_status_service(
    db: Session,
    order_id: int,
    new_status: OrderStatus
):
    order = get_order(
        db=db,
        order_id=order_id
    )

    if order is None:
        raise ValueError("Order not found")

    allowed_transitions = {
        OrderStatus.PENDING: [
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED
        ],
        OrderStatus.CONFIRMED: [
            OrderStatus.PROCESSING,
            OrderStatus.CANCELLED
        ],
        OrderStatus.PROCESSING: [
            OrderStatus.SHIPPED
        ],
        OrderStatus.SHIPPED: [
            OrderStatus.DELIVERED
        ],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: []
    }

    current_status = OrderStatus(order.status)

    if new_status not in allowed_transitions[current_status]:
        raise ValueError(
            f"Cannot change order status "
            f"from {current_status} to {new_status}"
        )

    return update_order_status(
        db=db,
        order_id=order_id,
        status=new_status
    )

def cancel_order_service(
    db: Session,
    order_id: int,
    current_user: dict,
    token: str
):
    order = get_order(
        db=db,
        order_id=order_id
    )

    if order is None:
        raise ValueError("Order not found")


    if (
        current_user["role"] != "admin"
        and order.user_id != current_user["id"]
    ):
        raise PermissionError(
            "You are not allowed to cancel this order"
        )

    
    allowed_cancel_statuses = [
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED
    ]
    
    current_status = OrderStatus(order.status)

    if current_status not in allowed_cancel_statuses:
     raise ValueError(
        f"Order cannot be cancelled from "
        f"{current_status.value} status"
    )


    for item in order.items:

        restored_product = restore_product_stock(
            product_id=item.product_id,
            quantity=item.quantity,
            token=token
        )

        if restored_product is None:
            raise ValueError(
                f"Product {item.product_id} not found"
            )

    order.status = "cancelled"

    db.commit()
    db.refresh(order)

    return order