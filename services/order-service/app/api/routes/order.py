from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderStatus
from app.core.security import get_current_user
from app.core.security import (
    get_current_user,
    oauth2_scheme,
    require_admin,
    require_payment_service
)
from app.services.order_service import (
    create_order_service,
    get_my_orders_service,
    get_order_service,
    update_order_status_service,
    cancel_order_service
)

router = APIRouter()

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=201
)
def create_order_route(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        created_order = create_order_service(
            db=db,
            user_id=current_user["id"],
            items=order.items,
            token=token
        )

        return created_order

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )




@router.get(
    "/my",
    response_model=list[OrderResponse]
)
def get_my_orders_route(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return  get_my_orders_service(
        db=db,
        current_user=current_user
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order_route(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return get_order_service(
            db=db,
            order_id=order_id,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse
)
def update_order_status_route(
    order_id: int,
    status_update: OrderStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        return update_order_status_service(
            db=db,
            order_id=order_id,
            new_status=status_update
        ) 

    except ValueError as e:
        if str(e) == "Order not found":
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse
)
def cancel_order_route(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        return cancel_order_service(
            db=db,
            order_id=order_id,
            current_user=current_user,
            token=token
        )

    except ValueError as e:
        if str(e) == "Order not found":
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )


@router.patch(
    "/{order_id}/payment-confirm",
    response_model=OrderResponse
)
def payment_confirm_order_route(
    order_id: int,
    db: Session = Depends(get_db),
    _service=Depends(require_payment_service)
):
    try:
        return update_order_status_service(
            db=db,
            order_id=order_id,
            new_status=OrderStatus.CONFIRMED
        )

    except ValueError as e:
        if str(e) == "Order not found":
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )