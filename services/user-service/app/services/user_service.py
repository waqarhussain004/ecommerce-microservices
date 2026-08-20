from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    create_user as create_user_repository,
    get_users as get_users_repository,
    get_user_by_id as get_user_by_id_repository,
    update_user as update_user_repository,
    delete_user as delete_user_repository
)


def create_user(db: Session, user_data):
    return create_user_repository(db, user_data)

def get_users(db: Session):
    return get_users_repository(db)

def get_user_by_id(db: Session, user_id: int):
    return get_user_by_id_repository(db, user_id)

def update_user(db: Session, user_id: int, user_data):
    return update_user_repository(db, user_id, user_data)

def delete_user(db: Session, user_id: int):
    return delete_user_repository(db, user_id)