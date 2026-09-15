from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.user import User, Role, UserRole
from app.schemas.user import UserResponse, UserUpdate, RoleAssign

router = APIRouter(prefix="/api/admin/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return (
        db.query(User)
        .options(joinedload(User.roles))
        .order_by(User.user_id)
        .all()
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(joinedload(User.roles))
        .filter(User.user_id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/roles", response_model=UserResponse, status_code=201)
def assign_role(user_id: int, payload: RoleAssign, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")

    role = db.query(Role).filter(Role.role_id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="역할을 찾을 수 없습니다.")

    exists = (
        db.query(UserRole)
        .filter_by(user_id=user_id, role_id=payload.role_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="이미 부여된 역할입니다.")

    db.add(UserRole(user_id=user_id, role_id=payload.role_id))
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}/roles/{role_id}", response_model=UserResponse)
def remove_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user_role = (
        db.query(UserRole)
        .filter_by(user_id=user_id, role_id=role_id)
        .first()
    )
    if not user_role:
        raise HTTPException(status_code=404, detail="해당 역할이 부여되어 있지 않습니다.")

    db.delete(user_role)
    db.commit()

    user = db.query(User).filter(User.user_id == user_id).first()
    db.refresh(user)
    return user