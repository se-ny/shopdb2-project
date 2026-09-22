import uuid

from sqlalchemy.orm import Session

from app.models.admin_log import AdminActionLog


def _generate_log_code() -> str:
    return f"LOG-{uuid.uuid4().hex[:16].upper()}"


def log_admin_action(
    db: Session,
    *,
    admin_user_id: int,
    action_type: str,
    target_table: str,
    target_id: int | None = None,
    org_id: int | None = None,
    before_value: dict | None = None,
    after_value: dict | None = None,
) -> AdminActionLog:
    """관리자 처리 이력을 admin_action_logs에 기록합니다.

    이 함수 안에서는 db.add()만 하고 commit은 하지 않습니다.
    호출하는 라우터의 db.commit()에 같이 실려서, 원래 처리(예: 조직 수정)와
    로그 기록이 하나의 트랜잭션으로 묶입니다. 즉 조직 수정이 실패해서
    rollback되면 로그도 같이 안 남고, 성공하면 둘 다 같이 저장됩니다.
    """
    log = AdminActionLog(
        log_code=_generate_log_code(),
        admin_user_id=admin_user_id,
        org_id=org_id,
        action_type=action_type,
        target_table=target_table,
        target_id=target_id,
        before_value=before_value,
        after_value=after_value,
    )
    db.add(log)
    return log