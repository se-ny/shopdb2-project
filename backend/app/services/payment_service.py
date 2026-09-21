import json
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.repositories import payment_repository
from app.schemas.payment import (
    PaymentCreate,
    PaymentTransactionCreate,
    PaymentUpdate,
    PaymentWebhookCreate,
)


ALLOWED_TRANSACTION_TYPES = {
    "REQUEST",
    "APPROVE",
    "CANCEL",
    "PARTIAL_CANCEL",
    "REFUND",
}


class PaymentServiceError(Exception):
    """결제 서비스 공통 오류."""


class PaymentNotFoundError(PaymentServiceError):
    """결제 정보를 찾을 수 없는 경우."""


class PaymentValidationError(PaymentServiceError):
    """결제 요청 값이 올바르지 않은 경우."""

def _get_owned_order(
    db: Session,
    order_id: int,
    buyer_user_id: int,
):
    order = payment_repository.get_order_for_payment(
        db,
        order_id,
    )

    if order is None:
        raise PaymentNotFoundError(
            "주문 정보를 찾을 수 없습니다."
        )

    if int(order["buyer_user_id"]) != buyer_user_id:
        raise PaymentValidationError(
            "다른 구매자의 주문에 대한 결제는 처리할 수 없습니다."
        )

    return order


def _validate_payment_owner(
    db: Session,
    payment,
    buyer_user_id: int,
):
    order = _get_owned_order(
        db,
        int(payment["order_id"]),
        buyer_user_id,
    )

    return order

def _json_to_db(value: Any):
    """
    raw SQL(text)에서 MySQL JSON 컬럼에 저장할 수 있도록
    dict/list를 JSON 문자열로 변환한다.
    """
    if value is None:
        return None

    if isinstance(value, str):
        return value

    return json.dumps(
        value,
        ensure_ascii=False,
    )


def _json_from_db(value: Any):
    """
    MySQL JSON 결과가 문자열로 반환되는 경우
    Python dict/list로 복원한다.
    """
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def _normalize_transaction(row):
    if row is None:
        return None

    data = dict(row)

    data["request_json"] = _json_from_db(
        data.get("request_json")
    )
    data["response_json"] = _json_from_db(
        data.get("response_json")
    )

    return data


def _normalize_webhook(row):
    if row is None:
        return None

    data = dict(row)

    data["payload_json"] = _json_from_db(
        data.get("payload_json")
    )

    return data


# =========================================================
# Payment 조회
# =========================================================

def get_payment(
    db: Session,
    payment_id: int,
    buyer_user_id: int | None = None,
):
    payment = payment_repository.get_payment_by_id(
        db,
        payment_id,
    )

    if payment is None:
        raise PaymentNotFoundError(
            "결제 정보를 찾을 수 없습니다."
        )

    if buyer_user_id is not None:
        _validate_payment_owner(
            db,
            payment,
            buyer_user_id,
        )

    return dict(payment)


def get_payments_by_order(
    db: Session,
    order_id: int,
    buyer_user_id: int,
):
    _get_owned_order(
        db,
        order_id,
        buyer_user_id,
    )

    rows = payment_repository.get_payments_by_order_id(
        db,
        order_id,
    )

    return [
        dict(row)
        for row in rows
    ]


# =========================================================
# Payment 생성
# =========================================================

def create_payment(
    db: Session,
    payload: PaymentCreate,
    buyer_user_id: int,
):
    data = payload.model_dump()
    order = _get_owned_order(
        db,
        data["order_id"],
        buyer_user_id,
    )

    if order["order_status"] not in {
        "ORDERED",
        "PAYMENT_PENDING",
    }:
        raise PaymentValidationError(
            "현재 주문 상태에서는 결제를 생성할 수 없습니다."
        )

    requested_amount = Decimal(
        str(data["requested_amount"])
    )
    order_total_amount = Decimal(
        str(order["total_amount"])
    )

    if requested_amount != order_total_amount:
        raise PaymentValidationError(
            "결제 요청 금액이 주문 금액과 일치하지 않습니다."
        )

    payment_key = data.get("payment_key")

    if payment_key:
        existing = (
            payment_repository
            .get_payment_by_payment_key(
                db,
                payment_key,
            )
        )

        if existing is not None:
            raise PaymentValidationError(
                "이미 등록된 payment_key입니다."
            )

    insert_data = {
        "order_id": data["order_id"],
        "pg_provider": data["pg_provider"],
        "payment_key": data.get("payment_key"),
        "pg_order_id": data.get("pg_order_id"),
        "customer_key": data.get("customer_key"),
        "payment_type": data.get("payment_type"),
        "payment_method": data.get(
            "payment_method"
        ),
        "payment_status": data.get(
            "payment_status"
        ),
        "requested_amount": data[
            "requested_amount"
        ],
        "approved_amount": Decimal("0.00"),
        "cancelled_amount": Decimal("0.00"),
        "balance_amount": Decimal("0.00"),
        "currency": data.get(
            "currency"
        ) or "KRW",
        "receipt_url": None,
        "requested_at": None,
        "approved_at": None,
        "cancelled_at": None,
    }

    try:
        payment_id = (
            payment_repository.create_payment(
                db,
                insert_data,
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return get_payment(
        db,
        payment_id,
    )


# =========================================================
# Payment 수정
# =========================================================

def update_payment(
    db: Session,
    payment_id: int,
    payload: PaymentUpdate,
    buyer_user_id: int | None = None,
):
    payment = payment_repository.get_payment_by_id(
        db,
        payment_id,
    )

    if payment is None:
        raise PaymentNotFoundError(
            "수정할 결제 정보를 찾을 수 없습니다."
        )

    if buyer_user_id is not None:

        _validate_payment_owner(db, payment, buyer_user_id)


    data = payload.model_dump(
        exclude_unset=True,
    )

    if not data:
        return dict(payment)

    new_payment_key = data.get(
        "payment_key"
    )

    if new_payment_key:
        existing = (
            payment_repository
            .get_payment_by_payment_key(
                db,
                new_payment_key,
            )
        )

        if (
            existing is not None
            and existing["payment_id"]
            != payment_id
        ):
            raise PaymentValidationError(
                "이미 사용 중인 payment_key입니다."
            )

    try:
        payment_repository.update_payment(
            db,
            payment_id,
            data,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return get_payment(
        db,
        payment_id,
    )


# =========================================================
# Payment Transaction
# =========================================================

def get_payment_transactions(
    db: Session,
    payment_id: int,
    buyer_user_id: int,
):
    payment = payment_repository.get_payment_by_id(
        db,
        payment_id,
    )

    if payment is None:
        raise PaymentNotFoundError(
            "결제 정보를 찾을 수 없습니다."
        )

    _validate_payment_owner(
        db,
        payment,
        buyer_user_id,
    )

    rows = payment_repository.get_transactions_by_payment_id(
        db,
        payment_id,
    )

    return [
        _normalize_transaction(row)
        for row in rows
    ]


def create_payment_transaction(
    db: Session,
    payment_id: int,
    payload: PaymentTransactionCreate,
    buyer_user_id: int,
):
    payment = payment_repository.get_payment_by_id(
        db,
        payment_id,
    )

    if payment is None:
        raise PaymentNotFoundError(
            "트랜잭션을 등록할 결제 정보가 없습니다."
        )
    _validate_payment_owner(
        db,
        payment,
        buyer_user_id,
    )

    data = payload.model_dump()

    transaction_type = data[
        "transaction_type"
    ].upper()

    if transaction_type not in ALLOWED_TRANSACTION_TYPES:
        raise PaymentValidationError(
            "transaction_type은 "
            "REQUEST, APPROVE, CANCEL, "
            "PARTIAL_CANCEL, REFUND 중 "
            "하나여야 합니다."
        )

    data["transaction_type"] = transaction_type

    idempotency_key = data.get(
        "idempotency_key"
    )

    # 같은 요청의 중복 실행 방지
    if idempotency_key:
        existing = (
            payment_repository
            .get_transaction_by_idempotency_key(
                db,
                idempotency_key,
            )
        )

        if existing is not None:
            return _normalize_transaction(
                existing
            )

    transaction_status = (
        data.get("transaction_status") or ""
    ).upper()

    transaction_amount = Decimal(
        str(data["transaction_amount"])
    )

    approved_amount = Decimal(
        str(payment["approved_amount"] or 0)
    )

    cancelled_amount = Decimal(
        str(payment["cancelled_amount"] or 0)
    )

    balance_amount = Decimal(
        str(payment["balance_amount"] or 0)
    )
    requested_amount = Decimal(
        str(payment["requested_amount"])
    )

    if (
        transaction_type == "APPROVE"
        and transaction_status == "SUCCESS"
    ):
        if payment["payment_status"] == "DONE":
            raise PaymentValidationError(
                "이미 승인 완료된 결제입니다."
            )

        if transaction_amount != requested_amount:
            raise PaymentValidationError(
                "승인 금액이 결제 요청 금액과 일치하지 않습니다."
            )
    # -----------------------------------------
    # 취소 금액 검증
    # -----------------------------------------
    if (
        transaction_type
        in {"CANCEL", "PARTIAL_CANCEL"}
        and transaction_status == "SUCCESS"
    ):
        if approved_amount <= 0:
            raise PaymentValidationError(
                "승인된 결제가 없어 취소할 수 없습니다."
            )

        if transaction_amount <= 0:
            raise PaymentValidationError(
                "취소 금액은 0보다 커야 합니다."
            )

        if transaction_amount > balance_amount:
            raise PaymentValidationError(
                "취소 금액이 남은 결제 금액보다 큽니다."
            )

        if (
            transaction_type == "CANCEL"
            and transaction_amount != balance_amount
        ):
            raise PaymentValidationError(
                "전체 취소 금액은 남은 결제 금액과 같아야 합니다."
            )

        if (
            transaction_type == "PARTIAL_CANCEL"
            and transaction_amount >= balance_amount
        ):
            raise PaymentValidationError(
                "부분 취소 금액은 남은 결제 금액보다 작아야 합니다."
            )

    data["request_json"] = _json_to_db(
        data.get("request_json")
    )

    data["response_json"] = _json_to_db(
        data.get("response_json")
    )

    try:
        transaction_id = (
            payment_repository.create_transaction(
                db,
                payment_id,
                data,
            )
        )

        # -------------------------------------
        # 결제 승인 성공
        # -------------------------------------
        if (
            transaction_type == "APPROVE"
            and transaction_status == "SUCCESS"
        ):
            payment_repository.mark_payment_approved(
                db,
                payment_id,
                transaction_amount,
            )

            payment_repository.update_order_status(
                db,
                payment["order_id"],
                "PAID",
            )

        # -------------------------------------
        # 전체 / 부분 취소 성공
        # -------------------------------------
        elif (
            transaction_type
            in {"CANCEL", "PARTIAL_CANCEL"}
            and transaction_status == "SUCCESS"
        ):
            new_cancelled_amount = (
                cancelled_amount
                + transaction_amount
            )

            new_balance_amount = (
                balance_amount
                - transaction_amount
            )

            if new_balance_amount == 0:
                new_payment_status = "CANCELED"

                payment_repository.update_order_status(
                    db,
                    payment["order_id"],
                    "CANCELLED",
                )

                payment_repository.release_order_reserved_inventory(
                    db,
                    payment["order_id"],
                )

            else:
                new_payment_status = (
                    "PARTIAL_CANCELED"
                )

            payment_repository.update_payment_cancel_amounts(
                db,
                payment_id,
                new_cancelled_amount,
                new_balance_amount,
                new_payment_status,
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    transaction = (
        payment_repository
        .get_transaction_by_id(
            db,
            transaction_id,
        )
    )

    return _normalize_transaction(
        transaction
    )