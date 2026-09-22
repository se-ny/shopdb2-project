import uuid

from sqlalchemy.orm import Session

from app.models.admin_log import AdminAlert


def _generate_alert_code() -> str:
    return f"ALT-{uuid.uuid4().hex[:16].upper()}"


def create_alert_if_not_exists(
    db: Session,
    *,
    alert_type: str,
    target_table: str,
    target_id: int,
    org_id: int | None = None,
    severity: str = "WARNING",
) -> AdminAlert | None:
    """같은 대상에 대해 아직 해결 안 된(resolved_yn='N') 알림이 있으면 새로 만들지 않습니다.

    체크 작업이 5분마다 도는데, 매번 새 알림을 쌓으면 같은 문제로 수십 개가
    생겨서 의미가 없어져요. 그래서 '이미 안 풀린 알림이 있는지' 먼저 확인하고,
    없을 때만 새로 만듭니다.
    """
    exists = (
        db.query(AdminAlert)
        .filter(
            AdminAlert.alert_type == alert_type,
            AdminAlert.target_table == target_table,
            AdminAlert.target_id == target_id,
            AdminAlert.resolved_yn == "N",
        )
        .first()
    )
    if exists:
        return None

    alert = AdminAlert(
        alert_code=_generate_alert_code(),
        org_id=org_id,
        alert_type=alert_type,
        target_table=target_table,
        target_id=target_id,
        severity=severity,
    )
    db.add(alert)
    return alert