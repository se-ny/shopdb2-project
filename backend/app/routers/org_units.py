from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.org_unit import OrgUnit
from app.schemas.org_unit import OrgUnitCreate, OrgUnitUpdate, OrgUnitResponse

router = APIRouter(prefix="/api/admin/orgs", tags=["조직관리"])


@router.get("", response_model=List[OrgUnitResponse])
def list_orgs(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    """전체 조직 목록 조회 (본사+지사)."""
    return db.query(OrgUnit).order_by(OrgUnit.org_id).all()


@router.get("/{org_id}", response_model=OrgUnitResponse)
def get_org(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    org = db.query(OrgUnit).filter(OrgUnit.org_id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="조직을 찾을 수 없습니다.")
    return org


@router.post("", response_model=OrgUnitResponse, status_code=201)
def create_org(
    payload: OrgUnitCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    org = OrgUnit(**payload.model_dump())
    db.add(org)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 존재하는 org_code입니다.")
    db.refresh(org)
    return org


@router.put("/{org_id}", response_model=OrgUnitResponse)
def update_org(
    org_id: int,
    payload: OrgUnitUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    org = db.query(OrgUnit).filter(OrgUnit.org_id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="조직을 찾을 수 없습니다.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)
    return org


@router.delete("/{org_id}", response_model=OrgUnitResponse)
def deactivate_org(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    """실제 삭제 대신 active_yn='N' 처리."""
    org = db.query(OrgUnit).filter(OrgUnit.org_id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="조직을 찾을 수 없습니다.")

    org.active_yn = "N"
    db.commit()
    db.refresh(org)
    return org