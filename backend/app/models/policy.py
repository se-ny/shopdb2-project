from sqlalchemy import (
    Column, BigInteger, String, Text, JSON, Date, DateTime,
    Enum, ForeignKey, UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


class CompanyPolicy(Base):
    __tablename__ = "company_policies"
    __table_args__ = (
        UniqueConstraint("policy_code", "policy_version", name="uk_policy_version"),
    )

    policy_id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("org_units.org_id"), nullable=True)
    policy_code = Column(String(50), nullable=False)
    policy_name = Column(String(200), nullable=False)
    policy_version = Column(String(30), nullable=False)
    policy_type = Column(String(50), nullable=True)
    policy_content = Column(Text, nullable=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    active_yn = Column(String(1), default="Y")
    created_at = Column(DateTime, server_default=func.now())


class RefundPolicy(Base):
    __tablename__ = "refund_policies"

    refund_policy_id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("org_units.org_id"), nullable=True)
    policy_name = Column(String(200), nullable=False)
    allowed_days = Column(BigInteger, nullable=False)
    unopened_refund_yn = Column(String(1), default="Y")
    opened_refund_yn = Column(String(1), default="N")
    defective_refund_yn = Column(String(1), default="Y")
    shipping_fee_payer = Column(
        Enum("BUYER", "SELLER", "COMPANY", name="shipping_fee_payer_enum"),
        default="BUYER",
    )
    refund_policy_text = Column(Text, nullable=True)
    policy_json = Column(JSON, nullable=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    active_yn = Column(String(1), default="Y")