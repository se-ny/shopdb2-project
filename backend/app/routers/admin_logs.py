from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.admin_log import AdminActionLog
from app.models.user import User
from app.schemas.admin_log import AdminActionLogListResponse, AdminActionLogResponse

router = APIRouter(prefix="/api/admin/action-logs", tags=["관리자 활동 로그"])


@router.get("", response_model=AdminActionLogListResponse)
def list_action_logs(
    action_type: Optional[str] = Query(default=None),
    target_table: Optional[str] = Query(default=None),
    admin_user_id: Optional[int] = Query(default=None),
    org_id: Optional[int] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    query = (
        db.query(AdminActionLog, User.user_name)
        .join(User, User.user_id == AdminActionLog.admin_user_id)
    )

    if action_type:
        query = query.filter(AdminActionLog.action_type == action_type)
    if target_table:
        query = query.filter(AdminActionLog.target_table == target_table)
    if admin_user_id:
        query = query.filter(AdminActionLog.admin_user_id == admin_user_id)
    if org_id:
        query = query.filter(AdminActionLog.org_id == org_id)
    if date_from:
        query = query.filter(AdminActionLog.created_at >= date_from)
    if date_to:
        query = query.filter(AdminActionLog.created_at <= date_to)

    total = query.count()

    rows = (
        query.order_by(AdminActionLog.log_id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = []
    for log, admin_user_name in rows:
        item = AdminActionLogResponse.model_validate(log)
        item.admin_user_name = admin_user_name
        items.append(item)

    return AdminActionLogListResponse(total=total, items=items)


@router.get("/{log_id}", response_model=AdminActionLogResponse)
def get_action_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    row = (
        db.query(AdminActionLog, User.user_name)
        .join(User, User.user_id == AdminActionLog.admin_user_id)
        .filter(AdminActionLog.log_id == log_id)
        .first()
    )
    if row is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="로그를 찾을 수 없습니다.")

    log, admin_user_name = row
    item = AdminActionLogResponse.model_validate(log)
    item.admin_user_name = admin_user_name
    return item