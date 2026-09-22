from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.user import User, Role, UserRole
from app.schemas.user import UserResponse, UserUpdate, RoleAssign
from app.services.admin_log_service import log_admin_action

router = APIRouter(prefix="/api/admin/users", tags=["회원관리"])


@router.get("", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    return (
        db.query(User)
        .options(joinedload(User.roles))
        .order_by(User.user_id)
        .all()
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
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
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/roles", response_model=UserResponse, status_code=201)
def assign_role(
    user_id: int,
    payload: RoleAssign,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
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

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="ROLE_ASSIGN",
        target_table="user_roles",
        target_id=user.user_id,
        org_id=current_user.org_id,
        before_value=None,
        after_value={
            "user_id": user.user_id,
            "user_name": user.user_name,
            "role_id": role.role_id,
            "role_code": role.role_code,
            "role_name": role.role_name,
        },
    )

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}/roles/{role_id}", response_model=UserResponse)
def remove_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    user_role = (
        db.query(UserRole)
        .filter_by(user_id=user_id, role_id=role_id)
        .first()
    )
    if not user_role:
        raise HTTPException(status_code=404, detail="해당 역할이 부여되어 있지 않습니다.")

    user = db.query(User).filter(User.user_id == user_id).first()
    role = db.query(Role).filter(Role.role_id == role_id).first()

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="ROLE_REVOKE",
        target_table="user_roles",
        target_id=user_id,
        org_id=current_user.org_id,
        before_value={
            "user_id": user_id,
            "user_name": user.user_name if user else None,
            "role_id": role_id,
            "role_code": role.role_code if role else None,
            "role_name": role.role_name if role else None,
        },
        after_value=None,
    )

    db.delete(user_role)
    db.commit()

    db.refresh(user)
    return user