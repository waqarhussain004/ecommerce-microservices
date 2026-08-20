from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.db.models.user import User
from fastapi import HTTPException


def create_user(db: Session, user_data):
     
    if user_data.role == "admin":
        existing_admin = db.query(User).filter(
            User.role == "admin"
        ).first()

        if existing_admin:
            raise HTTPException(
                status_code=400,
                detail="Admin already exists"
            )
    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_users(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_data):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None

    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.id != user_id
    ).first()

    if existing_user:
        raise ValueError("Email already registered")

    user.name = user_data.name
    user.email = user_data.email
    user.password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None

    db.delete(user)
    db.commit()

    return user