from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.sql import func

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    order_id = Column(
        BigInteger,
        ForeignKey("orders.order_id"),
        nullable=False,
        index=True,
    )

    pg_provider = Column(
        String(50),
        nullable=False,
        index=True,
    )

    payment_key = Column(
        String(255),
        unique=True,
        nullable=True,
    )

    pg_order_id = Column(
        String(255),
        nullable=True,
    )

    customer_key = Column(
        String(255),
        nullable=True,
    )

    payment_type = Column(
        String(50),
        nullable=True,
    )

    payment_method = Column(
        String(100),
        nullable=True,
    )

    payment_status = Column(
        String(50),
        nullable=True,
    )

    requested_amount = Column(
        Numeric(15, 2),
        nullable=False,
    )

    approved_amount = Column(
        Numeric(15, 2),
        nullable=True,
        default=0,
    )

    cancelled_amount = Column(
        Numeric(15, 2),
        nullable=True,
        default=0,
    )

    balance_amount = Column(
        Numeric(15, 2),
        nullable=True,
        default=0,
    )

    currency = Column(
        String(10),
        nullable=True,
        default="KRW",
    )

    receipt_url = Column(
        String(2000),
        nullable=True,
    )

    requested_at = Column(
        DateTime,
        nullable=True,
    )

    approved_at = Column(
        DateTime,
        nullable=True,
    )

    cancelled_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )