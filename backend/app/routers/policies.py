from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.policy import CompanyPolicy, RefundPolicy
from app.schemas.policy import (
    CompanyPolicyCreate, CompanyPolicyUpdate, CompanyPolicyResponse,
    RefundPolicyCreate, RefundPolicyUpdate, RefundPolicyResponse,
)
from app.services.admin_log_service import log_admin_action

router = APIRouter(prefix="/api/admin/policies", tags=["정책관리"])


def _company_policy_snapshot(policy: CompanyPolicy) -> dict:
    return {
        "policy_name": policy.policy_name,
        "policy_version": policy.policy_version,
        "policy_type": policy.policy_type,
        "policy_content": policy.policy_content,
        "effective_from": str(policy.effective_from),
        "effective_to": str(policy.effective_to) if policy.effective_to else None,
    }


def _refund_policy_snapshot(policy: RefundPolicy) -> dict:
    return {
        "policy_name": policy.policy_name,
        "allowed_days": policy.allowed_days,
        "unopened_refund_yn": policy.unopened_refund_yn,
        "opened_refund_yn": policy.opened_refund_yn,
        "defective_refund_yn": policy.defective_refund_yn,
        "shipping_fee_payer": policy.shipping_fee_payer,
        "effective_from": str(policy.effective_from),
        "effective_to": str(policy.effective_to) if policy.effective_to else None,
    }


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
    db.flush()

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="POLICY_CREATE",
        target_table="company_policies",
        target_id=policy.policy_id,
        org_id=policy.org_id,
        before_value=None,
        after_value=_company_policy_snapshot(policy),
    )

    db.commit()
    db.refresh(policy)
    return policy


@router.put("/company/{policy_id}", response_model=CompanyPolicyResponse)
def update_company_policy(
    policy_id: int,
    payload: CompanyPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    policy = db.query(CompanyPolicy).filter(CompanyPolicy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다.")

    before = _company_policy_snapshot(policy)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)

    after = _company_policy_snapshot(policy)

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="POLICY_UPDATE",
        target_table="company_policies",
        target_id=policy.policy_id,
        org_id=policy.org_id,
        before_value=before,
        after_value=after,
    )

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

    before = {"active_yn": policy.active_yn}
    policy.active_yn = "N"
    after = {"active_yn": policy.active_yn}

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="POLICY_EXPIRE",
        target_table="company_policies",
        target_id=policy.policy_id,
        org_id=policy.org_id,
        before_value=before,
        after_value=after,
    )

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
    db.flush()

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="POLICY_CREATE",
        target_table="refund_policies",
        target_id=policy.refund_policy_id,
        org_id=policy.org_id,
        before_value=None,
        after_value=_refund_policy_snapshot(policy),
    )

    db.commit()
    db.refresh(policy)
    return policy


@router.put("/refund/{refund_policy_id}", response_model=RefundPolicyResponse)
def update_refund_policy(
    refund_policy_id: int,
    payload: RefundPolicyUpdate,
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

    before = _refund_policy_snapshot(policy)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)

    after = _refund_policy_snapshot(policy)

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="POLICY_UPDATE",
        target_table="refund_policies",
        target_id=policy.refund_policy_id,
        org_id=policy.org_id,
        before_value=before,
        after_value=after,
    )

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

    before = {"active_yn": policy.active_yn}
    policy.active_yn = "N"
    after = {"active_yn": policy.active_yn}

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="POLICY_EXPIRE",
        target_table="refund_policies",
        target_id=policy.refund_policy_id,
        org_id=policy.org_id,
        before_value=before,
        after_value=after,
    )

    db.commit()
    db.refresh(policy)
    return policy