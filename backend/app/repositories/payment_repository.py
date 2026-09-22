from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


PAYMENT_COLUMNS = """
    payment_id,
    order_id,
    pg_provider,
    payment_key,
    pg_order_id,
    customer_key,
    payment_type,
    payment_method,
    payment_status,
    requested_amount,
    approved_amount,
    cancelled_amount,
    balance_amount,
    currency,
    receipt_url,
    requested_at,
    approved_at,
    cancelled_at,
    created_at
"""


TRANSACTION_COLUMNS = """
    transaction_id,
    payment_id,
    transaction_key,
    transaction_type,
    transaction_status,
    transaction_amount,
    pg_transaction_id,
    idempotency_key,
    cancel_reason,
    request_json,
    response_json,
    created_at
"""


WEBHOOK_COLUMNS = """
    webhook_id,
    payment_id,
    pg_provider,
    event_type,
    event_id,
    payload_json,
    processed_yn,
    error_message,
    received_at,
    processed_at
"""


def get_payment_by_id(
    db: Session,
    payment_id: int,
):
    row = db.execute(
        text(
            f"""
            SELECT
                {PAYMENT_COLUMNS}
            FROM payments
            WHERE payment_id = :payment_id
            """
        ),
        {
            "payment_id": payment_id,
        },
    ).mappings().first()

    return row


def get_payment_by_payment_key(
    db: Session,
    payment_key: str,
):
    row = db.execute(
        text(
            f"""
            SELECT
                {PAYMENT_COLUMNS}
            FROM payments
            WHERE payment_key = :payment_key
            """
        ),
        {
            "payment_key": payment_key,
        },
    ).mappings().first()

    return row


def get_payments_by_order_id(
    db: Session,
    order_id: int,
):
    rows = db.execute(
        text(
            f"""
            SELECT
                {PAYMENT_COLUMNS}
            FROM payments
            WHERE order_id = :order_id
            ORDER BY payment_id DESC
            """
        ),
        {
            "order_id": order_id,
        },
    ).mappings().all()

    return rows

def get_order_for_payment(
    db: Session,
    order_id: int,
):
    row = db.execute(
        text(
            """
            SELECT
                order_id,
                buyer_user_id,
                order_status,
                total_amount
            FROM orders
            WHERE order_id = :order_id
            """
        ),
        {
            "order_id": order_id,
        },
    ).mappings().first()

    return row

def create_payment(
    db: Session,
    data: dict,
):
    result = db.execute(
        text(
            """
            INSERT INTO payments
            (
                order_id,
                pg_provider,
                payment_key,
                pg_order_id,
                customer_key,
                payment_type,
                payment_method,
                payment_status,
                requested_amount,
                approved_amount,
                cancelled_amount,
                balance_amount,
                currency,
                receipt_url,
                requested_at,
                approved_at,
                cancelled_at
            )
            VALUES
            (
                :order_id,
                :pg_provider,
                :payment_key,
                :pg_order_id,
                :customer_key,
                :payment_type,
                :payment_method,
                :payment_status,
                :requested_amount,
                :approved_amount,
                :cancelled_amount,
                :balance_amount,
                :currency,
                :receipt_url,
                :requested_at,
                :approved_at,
                :cancelled_at
            )
            """
        ),
        data,
    )

    return result.lastrowid


def update_payment(
    db: Session,
    payment_id: int,
    data: dict,
):
    if not data:
        return

    allowed_fields = {
        "payment_key",
        "pg_order_id",
        "customer_key",
        "payment_type",
        "payment_method",
        "payment_status",
        "approved_amount",
        "cancelled_amount",
        "balance_amount",
        "receipt_url",
        "requested_at",
        "approved_at",
        "cancelled_at",
    }

    fields = []
    params = {
        "payment_id": payment_id,
    }

    for key, value in data.items():
        if key not in allowed_fields:
            continue

        fields.append(
            f"{key} = :{key}"
        )
        params[key] = value

    if not fields:
        return

    db.execute(
        text(
            f"""
            UPDATE payments
            SET {", ".join(fields)}
            WHERE payment_id = :payment_id
            """
        ),
        params,
    )


def create_transaction(
    db: Session,
    payment_id: int,
    data: dict,
):
    params = {
        "payment_id": payment_id,
        **data,
    }

    result = db.execute(
        text(
            """
            INSERT INTO payment_transactions
            (
                payment_id,
                transaction_key,
                transaction_type,
                transaction_status,
                transaction_amount,
                pg_transaction_id,
                idempotency_key,
                cancel_reason,
                request_json,
                response_json
            )
            VALUES
            (
                :payment_id,
                :transaction_key,
                :transaction_type,
                :transaction_status,
                :transaction_amount,
                :pg_transaction_id,
                :idempotency_key,
                :cancel_reason,
                :request_json,
                :response_json
            )
            """
        ),
        params,
    )

    return result.lastrowid


def get_transaction_by_id(
    db: Session,
    transaction_id: int,
):
    row = db.execute(
        text(
            f"""
            SELECT
                {TRANSACTION_COLUMNS}
            FROM payment_transactions
            WHERE transaction_id = :transaction_id
            """
        ),
        {
            "transaction_id": transaction_id,
        },
    ).mappings().first()

    return row


def get_transactions_by_payment_id(
    db: Session,
    payment_id: int,
):
    rows = db.execute(
        text(
            f"""
            SELECT
                {TRANSACTION_COLUMNS}
            FROM payment_transactions
            WHERE payment_id = :payment_id
            ORDER BY created_at DESC,
                     transaction_id DESC
            """
        ),
        {
            "payment_id": payment_id,
        },
    ).mappings().all()

    return rows


def get_transaction_by_idempotency_key(
    db: Session,
    idempotency_key: str,
):
    row = db.execute(
        text(
            f"""
            SELECT
                {TRANSACTION_COLUMNS}
            FROM payment_transactions
            WHERE idempotency_key = :idempotency_key
            ORDER BY transaction_id DESC
            LIMIT 1
            """
        ),
        {
            "idempotency_key": idempotency_key,
        },
    ).mappings().first()

    return row


def create_webhook_event(
    db: Session,
    data: dict,
):
    result = db.execute(
        text(
            """
            INSERT INTO payment_webhook_events
            (
                payment_id,
                pg_provider,
                event_type,
                event_id,
                payload_json,
                processed_yn,
                error_message,
                processed_at
            )
            VALUES
            (
                :payment_id,
                :pg_provider,
                :event_type,
                :event_id,
                :payload_json,
                :processed_yn,
                :error_message,
                :processed_at
            )
            """
        ),
        data,
    )

    return result.lastrowid


def get_webhook_by_event_id(
    db: Session,
    event_id: str,
):
    row = db.execute(
        text(
            f"""
            SELECT
                {WEBHOOK_COLUMNS}
            FROM payment_webhook_events
            WHERE event_id = :event_id
            ORDER BY webhook_id DESC
            LIMIT 1
            """
        ),
        {
            "event_id": event_id,
        },
    ).mappings().first()

    return row


def get_webhook_by_id(
    db: Session,
    webhook_id: int,
):
    row = db.execute(
        text(
            f"""
            SELECT
                {WEBHOOK_COLUMNS}
            FROM payment_webhook_events
            WHERE webhook_id = :webhook_id
            """
        ),
        {
            "webhook_id": webhook_id,
        },
    ).mappings().first()

    return row


def mark_webhook_processed(
    db: Session,
    webhook_id: int,
    processed_yn: str,
    error_message: Optional[str] = None,
):
    db.execute(
        text(
            """
            UPDATE payment_webhook_events
            SET
                processed_yn = :processed_yn,
                error_message = :error_message,
                processed_at = CURRENT_TIMESTAMP
            WHERE webhook_id = :webhook_id
            """
        ),
        {
            "webhook_id": webhook_id,
            "processed_yn": processed_yn,
            "error_message": error_message,
        },
    )


def mark_payment_approved(
    db: Session,
    payment_id: int,
    approved_amount,
):
    db.execute(
        text(
            """
            UPDATE payments
            SET
                payment_status = 'DONE',
                approved_amount = :approved_amount,
                balance_amount = :approved_amount,
                approved_at = CURRENT_TIMESTAMP
            WHERE payment_id = :payment_id
            """
        ),
        {
            "payment_id": payment_id,
            "approved_amount": approved_amount,
        },
    )


def update_order_status(
    db: Session,
    order_id: int,
    order_status: str,
):
    db.execute(
        text(
            """
            UPDATE orders
            SET
                order_status = :order_status,
                updated_at = CURRENT_TIMESTAMP
            WHERE order_id = :order_id
            """
        ),
        {
            "order_id": order_id,
            "order_status": order_status,
        },
    )

def update_payment_cancel_amounts(
    db: Session,
    payment_id: int,
    cancelled_amount,
    balance_amount,
    payment_status: str,
):
    db.execute(
        text(
            """
            UPDATE payments
            SET
                cancelled_amount = :cancelled_amount,
                balance_amount = :balance_amount,
                payment_status = :payment_status,
                cancelled_at = CASE
                    WHEN :balance_amount = 0
                    THEN CURRENT_TIMESTAMP
                    ELSE cancelled_at
                END
            WHERE payment_id = :payment_id
            """
        ),
        {
            "payment_id": payment_id,
            "cancelled_amount": cancelled_amount,
            "balance_amount": balance_amount,
            "payment_status": payment_status,
        },
    )

def release_order_reserved_inventory(
    db: Session,
    order_id: int,
):
    items = db.execute(
        text(
            """
            SELECT
                oi.order_item_id,
                oi.variant_id,
                oi.quantity,
                i.inventory_id,
                i.stock_quantity,
                i.reserved_quantity
            FROM orders o
            JOIN order_items oi
                ON oi.order_id = o.order_id
            JOIN inventories i
                ON i.org_id = o.org_id
               AND i.variant_id = oi.variant_id
            WHERE o.order_id = :order_id
            FOR UPDATE
            """
        ),
        {
            "order_id": order_id,
        },
    ).mappings().all()

    for item in items:
        quantity = int(item["quantity"])

        stock_before = int(
            item["stock_quantity"]
        )
        reserved_before = int(
            item["reserved_quantity"]
        )

        if reserved_before < quantity:
            raise ValueError(
                "예약재고가 주문수량보다 적어 "
                "재고를 해제할 수 없습니다."
            )

        reserved_after = (
            reserved_before - quantity
        )

        # 실제 재고는 변경하지 않음
        stock_after = stock_before

        db.execute(
            text(
                """
                UPDATE inventories
                SET reserved_quantity = :reserved_after
                WHERE inventory_id = :inventory_id
                """
            ),
            {
                "inventory_id":
                    item["inventory_id"],
                "reserved_after":
                    reserved_after,
            },
        )

        db.execute(
            text(
                """
                INSERT INTO inventory_movements
                (
                    inventory_id,
                    movement_type,
                    quantity_change,
                    stock_before,
                    stock_after,
                    reserved_before,
                    reserved_after,
                    reference_type,
                    reference_id,
                    reason,
                    changed_by_user_id
                )
                VALUES
                (
                    :inventory_id,
                    'RELEASE',
                    0,
                    :stock_before,
                    :stock_after,
                    :reserved_before,
                    :reserved_after,
                    'ORDER',
                    :order_id,
                    '결제 전체 취소로 예약재고 해제',
                    NULL
                )
                """
            ),
            {
                "inventory_id":
                    item["inventory_id"],
                "stock_before":
                    stock_before,
                "stock_after":
                    stock_after,
                "reserved_before":
                    reserved_before,
                "reserved_after":
                    reserved_after,
                "order_id":
                    order_id,
            },
        )


def list_payments_admin(
    db: Session,
    payment_status: str | None = None,
    skip: int = 0,
    limit: int = 20,
):
    where_clause = ""
    params = {"skip": skip, "limit": limit}

    if payment_status:
        where_clause = "WHERE p.payment_status = :payment_status"
        params["payment_status"] = payment_status

    rows = db.execute(
        text(
            f"""
            SELECT
                p.payment_id, p.order_id, o.order_no, u.user_name AS buyer_name,
                p.pg_provider, p.payment_status,
                p.requested_amount, p.approved_amount,
                p.cancelled_amount, p.balance_amount, p.created_at
            FROM payments p
            JOIN orders o ON o.order_id = p.order_id
            JOIN users u ON u.user_id = o.buyer_user_id
            {where_clause}
            ORDER BY p.payment_id DESC
            LIMIT :limit OFFSET :skip
            """
        ),
        params,
    ).mappings().all()

    total = db.execute(
        text(
            f"""
            SELECT COUNT(*) AS cnt
            FROM payments p
            {where_clause}
            """
        ),
        {k: v for k, v in params.items() if k not in ("skip", "limit")},
    ).scalar()

    return rows, total