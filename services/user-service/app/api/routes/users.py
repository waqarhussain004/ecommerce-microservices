from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse , UserUpdate
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.user_service import (
    create_user,
    get_users,
    get_user_by_id,
    update_user,
    delete_user
)

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user=Depends(get_current_user)
):
    return current_user


# @router.post("/", response_model=UserResponse)
# def create_user_route(
#     user: UserCreate,
#     db: Session = Depends(get_db)
# ):
#     return create_user(db, user)


@router.get("/", response_model=list[UserResponse])
def get_users_route(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_users(db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user_route(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own account"
        )
    
    try:
        updated_user = update_user(
        db,
        user_id,
        user
    )
    except ValueError as e:
        raise HTTPException(
        status_code=400,
        detail=str(e)
    )

    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return updated_user


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own account"
        )
    
    deleted_user = delete_user(db, user_id)

    if deleted_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return deleted_user



