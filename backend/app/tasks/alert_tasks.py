from datetime import datetime, timedelta

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.inventory import Inventory
from app.models.payment_webhook_event import PaymentWebhookEvent
from app.models.refund_request import RefundRequest
from app.services.admin_alert_service import create_alert_if_not_exists


def _check_low_stock(db):
    rows = db.query(Inventory).all()
    for inv in rows:
        available = inv.stock_quantity - inv.reserved_quantity - inv.safety_stock
        if available <= 0:
            create_alert_if_not_exists(
                db,
                alert_type="LOW_STOCK",
                target_table="inventories",
                target_id=inv.inventory_id,
                org_id=inv.org_id,
                severity="CRITICAL" if available < 0 else "WARNING",
            )


def _check_webhook_failed(db):
    rows = (
        db.query(PaymentWebhookEvent)
        .filter(
            PaymentWebhookEvent.processed_yn == "N",
            PaymentWebhookEvent.error_message.isnot(None),
        )
        .all()
    )
    for webhook in rows:
        create_alert_if_not_exists(
            db,
            alert_type="WEBHOOK_FAILED",
            target_table="payment_webhook_events",
            target_id=webhook.webhook_id,
            org_id=None,
            severity="CRITICAL",
        )


def _check_refund_delayed(db):
    threshold = datetime.utcnow() - timedelta(days=settings.refund_delay_alert_days)
    rows = (
        db.query(RefundRequest)
        .filter(
            RefundRequest.refund_status.in_(["REQUESTED", "REVIEWING"]),
            RefundRequest.requested_at <= threshold,
        )
        .all()
    )
    for refund in rows:
        create_alert_if_not_exists(
            db,
            alert_type="REFUND_DELAYED",
            target_table="refund_requests",
            target_id=refund.refund_request_id,
            org_id=None,
            severity="WARNING",
        )


@celery_app.task(name="app.tasks.alert_tasks.run_alert_checks")
def run_alert_checks():
    db = SessionLocal()
    try:
        _check_low_stock(db)
        _check_webhook_failed(db)
        _check_refund_delayed(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()