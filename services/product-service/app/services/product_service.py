from sqlalchemy.orm import Session

from app.db.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories import product_repository


def create_product(
    db: Session,
    product_data: ProductCreate
):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock
    )

    return product_repository.create(db, product)


def get_products(db: Session):
    return product_repository.get_all(db)


def get_product(
    db: Session,
    product_id: int
):
    return product_repository.get_by_id(
        db,
        product_id
    )


def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate
):
    product = product_repository.get_by_id(
        db,
        product_id
    )

    if product is None:
        return None

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.price is not None:
        product.price = product_data.price

    if product_data.stock is not None:
        product.stock = product_data.stock

    return product_repository.update(db, product)


def delete_product(
    db: Session,
    product_id: int
):
    product = product_repository.get_by_id(
        db,
        product_id
    )

    if product is None:
        return None

    return product_repository.delete(db, product)


def reduce_product_stock(
    db: Session,
    product_id: int,
    quantity: int
):
    return product_repository.reduce_stock(
        db,
        product_id,
        quantity
    )


def restore_product_stock(
    db: Session,
    product_id: int,
    quantity: int
):
    return product_repository.restore_stock(
        db,
        product_id,
        quantity
    )