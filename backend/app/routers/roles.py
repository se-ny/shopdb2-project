from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import Role
from app.schemas.user import RoleResponse

router = APIRouter(prefix="/api/admin/roles", tags=["roles"])


@router.get("", response_model=List[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    """BUYER/SELLER/ADMIN 역할 마스터 목록."""
    return db.query(Role).order_by(Role.role_id).all()