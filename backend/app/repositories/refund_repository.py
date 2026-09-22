from sqlalchemy import text
from sqlalchemy.orm import Session


def list_refund_requests(
    db: Session,
    refund_status: str | None = None,
    skip: int = 0,
    limit: int = 20,
):
    where_clause = ""
    params = {"skip": skip, "limit": limit}

    if refund_status:
        where_clause = "WHERE r.refund_status = :refund_status"
        params["refund_status"] = refund_status

    rows = db.execute(
        text(
            f"""
            SELECT
                r.refund_request_id, r.order_id, o.order_no, u.user_name AS buyer_name,
                r.refund_reason, r.requested_amount, r.approved_amount,
                r.refund_status, r.requested_at, r.approved_at, r.completed_at
            FROM refund_requests r
            JOIN orders o ON o.order_id = r.order_id
            JOIN users u ON u.user_id = r.buyer_user_id
            {where_clause}
            ORDER BY r.refund_request_id DESC
            LIMIT :limit OFFSET :skip
            """
        ),
        params,
    ).mappings().all()

    total = db.execute(
        text(
            f"""
            SELECT COUNT(*) AS cnt
            FROM refund_requests r
            {where_clause}
            """
        ),
        {k: v for k, v in params.items() if k not in ("skip", "limit")},
    ).scalar()

    return rows, total