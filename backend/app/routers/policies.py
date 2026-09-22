from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.policy import CompanyPolicy, RefundPolicy
from app.schemas.policy import (
    CompanyPolicyCreate, CompanyPolicyResponse,
    RefundPolicyCreate, RefundPolicyResponse,
)

router = APIRouter(prefix="/api/admin/policies", tags=["정책관리"])


# ---------- 회사정책 ----------

@router.get("/company", response_model=List[CompanyPolicyResponse])
def list_company_policies(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    return db.query(CompanyPolicy).order_by(CompanyPolicy.policy_id).all()


@router.post("/company", response_model=CompanyPolicyResponse, status_code=201)
def create_company_policy(
    payload: CompanyPolicyCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    policy = CompanyPolicy(**payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.patch("/company/{policy_id}/expire", response_model=CompanyPolicyResponse)
def expire_company_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    """구버전 정책을 비활성화 처리."""
    policy = db.query(CompanyPolicy).filter(CompanyPolicy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다.")
    policy.active_yn = "N"
    db.commit()
    db.refresh(policy)
    return policy


# ---------- 환불정책 ----------

@router.get("/refund", response_model=List[RefundPolicyResponse])
def list_refund_policies(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    return db.query(RefundPolicy).order_by(RefundPolicy.refund_policy_id).all()


@router.post("/refund", response_model=RefundPolicyResponse, status_code=201)
def create_refund_policy(
    payload: RefundPolicyCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    policy = RefundPolicy(**payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.patch("/refund/{refund_policy_id}/expire", response_model=RefundPolicyResponse)
def expire_refund_policy(
    refund_policy_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    policy = (
        db.query(RefundPolicy)
        .filter(RefundPolicy.refund_policy_id == refund_policy_id)
        .first()
    )
    if not policy:
        raise HTTPException(status_code=404, detail="환불정책을 찾을 수 없습니다.")
    policy.active_yn = "N"
    db.commit()
    db.refresh(policy)
    return policy