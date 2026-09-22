from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.refund_request import RefundRequest
from app.repositories import payment_repository, refund_repository
from app.schemas.admin_payment import (
    RefundDecisionPayload,
    RefundRequestAdminResponse,
    PaymentAdminListResponse,
    RefundRequestAdminListResponse,
)
from app.services.admin_log_service import log_admin_action

router = APIRouter(prefix="/api/admin", tags=["결제/환불관리"])


# ---------- 목록 조회 ----------

@router.get("/payments", response_model=PaymentAdminListResponse)
def list_payments(
    payment_status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    rows, total = payment_repository.list_payments_admin(
        db, payment_status=payment_status, skip=skip, limit=limit
    )
    return {"total": total, "items": [dict(row) for row in rows]}


@router.get("/refunds", response_model=RefundRequestAdminListResponse)
def list_refunds(
    refund_status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    rows, total = refund_repository.list_refund_requests(
        db, refund_status=refund_status, skip=skip, limit=limit
    )
    return {"total": total, "items": [dict(row) for row in rows]}


# ---------- 결제 강제취소 ----------

@router.patch("/payments/{payment_id}/force-cancel")
def force_cancel_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    payment = payment_repository.get_payment_by_id(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="결제 정보를 찾을 수 없습니다.")

    if payment["payment_status"] == "CANCELED":
        raise HTTPException(status_code=400, detail="이미 취소된 결제입니다.")

    balance_amount = Decimal(str(payment["balance_amount"] or 0))
    if balance_amount <= 0:
        raise HTTPException(status_code=400, detail="취소할 남은 결제 금액이 없습니다.")

    cancelled_amount = Decimal(str(payment["cancelled_amount"] or 0)) + balance_amount

    before = {
        "payment_status": payment["payment_status"],
        "balance_amount": str(payment["balance_amount"]),
        "cancelled_amount": str(payment["cancelled_amount"]),
    }

    try:
        payment_repository.create_transaction(
            db,
            payment_id,
            {
                "transaction_key": None,
                "transaction_type": "CANCEL",
                "transaction_status": "SUCCESS",
                "transaction_amount": balance_amount,
                "pg_transaction_id": None,
                "idempotency_key": None,
                "cancel_reason": "관리자 강제 취소",
                "request_json": None,
                "response_json": None,
            },
        )

        payment_repository.update_payment_cancel_amounts(
            db, payment_id, cancelled_amount, Decimal("0"), "CANCELED",
        )

        payment_repository.update_order_status(
            db, payment["order_id"], "CANCELLED",
        )

        payment_repository.release_order_reserved_inventory(
            db, payment["order_id"],
        )

        after = {
            "payment_status": "CANCELED",
            "balance_amount": "0",
            "cancelled_amount": str(cancelled_amount),
        }

        log_admin_action(
            db,
            admin_user_id=current_user.user_id,
            action_type="PAYMENT_FORCE_CANCEL",
            target_table="payments",
            target_id=payment_id,
            org_id=None,
            before_value=before,
            after_value=after,
        )

        db.commit()
    except Exception:
        db.rollback()
        raise

    return payment_repository.get_payment_by_id(db, payment_id)


# ---------- 환불 승인 / 거절 ----------

def _refund_snapshot(refund: RefundRequest) -> dict:
    return {
        "refund_status": refund.refund_status,
        "approved_amount": str(refund.approved_amount) if refund.approved_amount is not None else None,
    }


@router.patch("/refunds/{refund_request_id}/approve", response_model=RefundRequestAdminResponse)
def approve_refund(
    refund_request_id: int,
    payload: RefundDecisionPayload,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    refund = db.query(RefundRequest).filter(
        RefundRequest.refund_request_id == refund_request_id
    ).first()
    if not refund:
        raise HTTPException(status_code=404, detail="환불 요청을 찾을 수 없습니다.")

    if refund.refund_status not in ("REQUESTED", "REVIEWING"):
        raise HTTPException(status_code=400, detail="이미 처리된 환불 요청입니다.")

    before = _refund_snapshot(refund)

    refund.refund_status = "APPROVED"
    refund.approved_amount = payload.approved_amount or refund.requested_amount
    from sqlalchemy.sql import func as sa_func
    refund.approved_at = sa_func.now()

    after = _refund_snapshot(refund)

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="REFUND_APPROVE",
        target_table="refund_requests",
        target_id=refund.refund_request_id,
        org_id=None,
        before_value=before,
        after_value=after,
    )

    db.commit()
    db.refresh(refund)
    return refund


@router.patch("/refunds/{refund_request_id}/reject", response_model=RefundRequestAdminResponse)
def reject_refund(
    refund_request_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    refund = db.query(RefundRequest).filter(
        RefundRequest.refund_request_id == refund_request_id
    ).first()
    if not refund:
        raise HTTPException(status_code=404, detail="환불 요청을 찾을 수 없습니다.")

    if refund.refund_status not in ("REQUESTED", "REVIEWING"):
        raise HTTPException(status_code=400, detail="이미 처리된 환불 요청입니다.")

    before = _refund_snapshot(refund)
    refund.refund_status = "REJECTED"
    after = _refund_snapshot(refund)

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="REFUND_REJECT",
        target_table="refund_requests",
        target_id=refund.refund_request_id,
        org_id=None,
        before_value=before,
        after_value=after,
    )

    db.commit()
    db.refresh(refund)
    return refund