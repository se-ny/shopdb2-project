from sqlalchemy import Column, BigInteger, String, Numeric, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    refund_request_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False)
    buyer_user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    refund_policy_id = Column(BigInteger, ForeignKey("refund_policies.refund_policy_id"), nullable=True)
    refund_reason = Column(String(500), nullable=True)
    requested_amount = Column(Numeric(15, 2), nullable=True)
    approved_amount = Column(Numeric(15, 2), nullable=True)
    refund_status = Column(
        Enum("REQUESTED", "REVIEWING", "APPROVED", "REJECTED", "COMPLETED", name="refund_status_enum"),
        default="REQUESTED",
    )
    requested_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)