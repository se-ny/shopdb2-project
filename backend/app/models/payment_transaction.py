from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    DateTime,
    ForeignKey,
    Numeric,
    JSON,
)
from sqlalchemy.sql import func

from app.core.database import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    transaction_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    payment_id = Column(
        BigInteger,
        ForeignKey("payments.payment_id"),
        nullable=False,
        index=True,
    )

    transaction_key = Column(
        String(255),
        nullable=True,
    )

    transaction_type = Column(
        Enum(
            "REQUEST",
            "APPROVE",
            "CANCEL",
            "PARTIAL_CANCEL",
            "REFUND",
            name="payment_transaction_type_enum",
        ),
        nullable=False,
    )

    transaction_status = Column(
        String(50),
        nullable=True,
    )

    transaction_amount = Column(
        Numeric(15, 2),
        nullable=False,
    )

    pg_transaction_id = Column(
        String(255),
        nullable=True,
    )

    idempotency_key = Column(
        String(255),
        nullable=True,
    )

    cancel_reason = Column(
        String(500),
        nullable=True,
    )

    request_json = Column(
        JSON,
        nullable=True,
    )

    response_json = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )