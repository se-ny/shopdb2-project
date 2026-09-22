from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.admin_log import AdminAlert
from app.schemas.admin_alert import AdminAlertListResponse, AdminAlertResponse

router = APIRouter(prefix="/api/admin/alerts", tags=["시스템 알림"])


@router.get("", response_model=AdminAlertListResponse)
def list_alerts(
    resolved_yn: Optional[str] = Query(default="N"),
    alert_type: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    query = db.query(AdminAlert)
    if resolved_yn:
        query = query.filter(AdminAlert.resolved_yn == resolved_yn)
    if alert_type:
        query = query.filter(AdminAlert.alert_type == alert_type)

    total = query.count()
    rows = (
        query.order_by(AdminAlert.alert_id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"total": total, "items": rows}


@router.patch("/{alert_id}/resolve", response_model=AdminAlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    alert = db.query(AdminAlert).filter(AdminAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")

    alert.resolved_yn = "Y"
    alert.resolved_by = current_user.user_id
    db.commit()
    db.refresh(alert)
    return alert