from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.sql import func

from app.core.database import Base


class PaymentWebhookEvent(Base):
    __tablename__ = "payment_webhook_events"

    webhook_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    payment_id = Column(
        BigInteger,
        ForeignKey("payments.payment_id"),
        nullable=True,
        index=True,
    )

    pg_provider = Column(
        String(50),
        nullable=True,
    )

    event_type = Column(
        String(100),
        nullable=True,
    )

    event_id = Column(
        String(255),
        nullable=True,
    )

    payload_json = Column(
        JSON,
        nullable=True,
    )

    processed_yn = Column(
        String(1),
        nullable=True,
        default="N",
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    received_at = Column(
        DateTime,
        server_default=func.now(),
    )

    processed_at = Column(
        DateTime,
        nullable=True,
    )