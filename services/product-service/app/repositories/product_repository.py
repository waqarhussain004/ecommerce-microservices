from sqlalchemy.orm import Session

from app.db.models.product import Product


def create(db: Session, product: Product):
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_all(db: Session):
    return db.query(Product).all()


def get_by_id(db: Session, product_id: int):
    return db.query(Product).filter(
        Product.id == product_id
    ).first()


def update(db: Session, product: Product):
    db.commit()
    db.refresh(product)

    return product


def delete(db: Session, product: Product):
    db.delete(product)
    db.commit()

    return product

def reduce_stock(
    db: Session,
    product_id: int,
    quantity: int
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        return None

    if product.stock < quantity:
        raise ValueError(
            f"Insufficient stock. Available stock: {product.stock}"
        )

    product.stock -= quantity

    db.commit()
    db.refresh(product)

    return product



def restore_stock(
    db: Session,
    product_id: int,
    quantity: int
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        return None

    product.stock += quantity

    db.commit()
    db.refresh(product)

    return product