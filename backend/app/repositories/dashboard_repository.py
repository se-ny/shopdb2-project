from sqlalchemy import text

from app.core.database import engine


def get_today_order_count() -> int:
    query = text("SELECT COUNT(*) FROM orders WHERE DATE(ordered_at) = CURDATE()")
    with engine.connect() as connection:
        return connection.execute(query).scalar() or 0


def get_today_revenue() -> float:
    query = text(
        """
        SELECT COALESCE(SUM(approved_amount), 0)
        FROM payments
        WHERE payment_status = 'DONE'
          AND DATE(approved_at) = CURDATE()
        """
    )
    with engine.connect() as connection:
        return float(connection.execute(query).scalar() or 0)


def get_recent_orders(limit: int = 5) -> list[dict]:
    query = text(
        """
        SELECT
            o.order_id, o.order_no, u.user_name AS buyer_name,
            o.order_status, o.total_amount, o.ordered_at
        FROM orders o
        JOIN users u ON u.user_id = o.buyer_user_id
        ORDER BY o.order_id DESC
        LIMIT :limit
        """
    )
    with engine.connect() as connection:
        rows = connection.execute(query, {"limit": limit}).mappings().all()
    return [dict(row) for row in rows]