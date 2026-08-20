from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse
)

from app.services.payment_service import (
    create_payment_service,
    process_payment_service,
    get_payment_service,
    get_my_payments_service
)

from app.core.security import (
    get_current_user,
    oauth2_scheme
)


router = APIRouter()


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=201
)
def create_payment_route(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        created_payment = create_payment_service(
            db=db,
            order_id=payment.order_id,
            user_id=current_user["id"],
            token=token
        )

        return created_payment

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

@router.get(
    "/my",
    response_model=list[PaymentResponse]
)
def get_my_payments_route(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_my_payments_service(
        db=db,
        current_user=current_user
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
def get_payment_route(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return get_payment_service(
            db=db,
            payment_id=payment_id,
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



# @router.patch(
#     "/{payment_id}/process",
#     response_model=PaymentResponse
# )
# def process_payment_route(
#     payment_id: int,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     try:
#         payment = process_payment_service(
#             db=db,
#             payment_id=payment_id,
#             user_id=current_user["id"]
#         )

#         return payment

#     except ValueError as e:
#         if str(e) == "Payment not found":
#             raise HTTPException(
#                 status_code=404,
#                 detail=str(e)
#             )

#         raise HTTPException(
#             status_code=400,
#             detail=str(e)
#         )

#     except PermissionError as e:
#         raise HTTPException(
#             status_code=403,
#             detail=str(e)
#         )