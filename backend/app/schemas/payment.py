from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# payments
# =========================================================

class PaymentCreate(BaseModel):
    order_id: int = Field(ge=1)
    pg_provider: str = Field(min_length=1, max_length=50)

    payment_key: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    pg_order_id: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    customer_key: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    payment_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    payment_method: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    payment_status: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    requested_amount: Decimal = Field(ge=0)

    currency: Optional[str] = Field(
        default="KRW",
        max_length=10,
    )


class PaymentUpdate(BaseModel):
    payment_key: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    pg_order_id: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    customer_key: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    payment_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    payment_method: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    payment_status: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    approved_amount: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )
    cancelled_amount: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )
    balance_amount: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    receipt_url: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    requested_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class PaymentOut(BaseModel):
    payment_id: int
    order_id: int
    pg_provider: str

    payment_key: Optional[str]
    pg_order_id: Optional[str]
    customer_key: Optional[str]
    payment_type: Optional[str]
    payment_method: Optional[str]
    payment_status: Optional[str]

    requested_amount: Decimal
    approved_amount: Optional[Decimal]
    cancelled_amount: Optional[Decimal]
    balance_amount: Optional[Decimal]

    currency: Optional[str]
    receipt_url: Optional[str]

    requested_at: Optional[datetime]
    approved_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
    )


# =========================================================
# payment_transactions
# =========================================================

class PaymentTransactionCreate(BaseModel):
    transaction_key: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    transaction_type: str

    transaction_status: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    transaction_amount: Decimal = Field(ge=0)

    pg_transaction_id: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    idempotency_key: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    cancel_reason: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    request_json: Optional[dict[str, Any]] = None
    response_json: Optional[dict[str, Any]] = None


class PaymentTransactionOut(BaseModel):
    transaction_id: int
    payment_id: int

    transaction_key: Optional[str]
    transaction_type: str
    transaction_status: Optional[str]
    transaction_amount: Decimal

    pg_transaction_id: Optional[str]
    idempotency_key: Optional[str]
    cancel_reason: Optional[str]

    request_json: Optional[dict[str, Any]]
    response_json: Optional[dict[str, Any]]

    created_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
    )


# =========================================================
# payment_webhook_events
# =========================================================

class PaymentWebhookCreate(BaseModel):
    payment_id: Optional[int] = Field(
        default=None,
        ge=1,
    )

    pg_provider: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    event_type: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    event_id: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    payload_json: Optional[dict[str, Any]] = None


class PaymentWebhookOut(BaseModel):
    webhook_id: int
    payment_id: Optional[int]

    pg_provider: Optional[str]
    event_type: Optional[str]
    event_id: Optional[str]

    payload_json: Optional[dict[str, Any]]

    processed_yn: Optional[str]
    error_message: Optional[str]

    received_at: Optional[datetime]
    processed_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
    )