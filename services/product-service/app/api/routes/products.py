from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    StockUpdate
)
from app.services.product_service import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
    reduce_product_stock,
    restore_product_stock
)

from app.core.security import( get_current_user , require_admin)


router = APIRouter()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=201
)
def create_product_route(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    return create_product(db, product)


@router.get(
    "/",
    response_model=list[ProductResponse]
)
def get_products_route(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    return get_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product_route(
    product_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    product = get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product_route(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    updated_product = update_product(
        db,
        product_id,
        product
    )

    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return updated_product


@router.delete(
    "/{product_id}",
    response_model=ProductResponse
)
def delete_product_route(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    deleted_product = delete_product(
        db,
        product_id
    )

    if deleted_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return deleted_product



@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse
)
def reduce_stock_route(
    product_id: int,
    stock_update: StockUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        updated_product = reduce_product_stock(
            db=db,
            product_id=product_id,
            quantity=stock_update.quantity
        )

        if updated_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return updated_product

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )



@router.patch(
    "/{product_id}/restore-stock",
    response_model=ProductResponse
)
def restore_stock_route(
    product_id: int,
    stock: StockUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    updated_product = restore_product_stock(
        db=db,
        product_id=product_id,
        quantity=stock.quantity
    )

    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return updated_product