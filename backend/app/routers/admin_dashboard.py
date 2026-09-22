from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.admin_log import AdminAlert
from app.models.refund_request import RefundRequest
from app.repositories import dashboard_repository
from app.schemas.admin_dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/api/admin/dashboard", tags=["대시보드"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    pending_refund_count = (
        db.query(RefundRequest)
        .filter(RefundRequest.refund_status.in_(["REQUESTED", "REVIEWING"]))
        .count()
    )

    unresolved_alert_count = (
        db.query(AdminAlert).filter(AdminAlert.resolved_yn == "N").count()
    )

    unresolved_critical_alert_count = (
        db.query(AdminAlert)
        .filter(AdminAlert.resolved_yn == "N", AdminAlert.severity == "CRITICAL")
        .count()
    )

    recent_alerts = (
        db.query(AdminAlert)
        .filter(AdminAlert.resolved_yn == "N")
        .order_by(AdminAlert.alert_id.desc())
        .limit(5)
        .all()
    )

    return {
        "today_order_count": dashboard_repository.get_today_order_count(),
        "today_revenue": dashboard_repository.get_today_revenue(),
        "pending_refund_count": pending_refund_count,
        "unresolved_alert_count": unresolved_alert_count,
        "unresolved_critical_alert_count": unresolved_critical_alert_count,
        "recent_orders": dashboard_repository.get_recent_orders(),
        "recent_alerts": recent_alerts,
    }