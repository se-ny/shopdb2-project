from sqlalchemy import Column, BigInteger, String, Enum, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class AdminActionLog(Base):
    __tablename__ = "admin_action_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    log_code = Column(String(50), unique=True, nullable=False)
    admin_user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    org_id = Column(BigInteger, ForeignKey("org_units.org_id"), nullable=True)
    action_type = Column(
        Enum(
            "ROLE_ASSIGN", "ROLE_REVOKE",
            "POLICY_CREATE", "POLICY_EXPIRE",
            "ORG_UPDATE", "ORG_DEACTIVATE",
            "PAYMENT_FORCE_CANCEL",
            "REFUND_APPROVE", "REFUND_REJECT",
            "PRODUCT_APPROVE", "PRODUCT_REJECT",
            name="admin_action_type_enum",
        ),
        nullable=False,
    )
    target_table = Column(String(50), nullable=False)
    target_id = Column(BigInteger, nullable=True)
    before_value = Column(JSON, nullable=True)
    after_value = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AdminAlert(Base):
    __tablename__ = "admin_alerts"

    alert_id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_code = Column(String(50), unique=True, nullable=False)
    org_id = Column(BigInteger, ForeignKey("org_units.org_id"), nullable=True)
    alert_type = Column(
        Enum("LOW_STOCK", "WEBHOOK_FAILED", "REFUND_DELAYED", name="admin_alert_type_enum"),
        nullable=False,
    )
    target_table = Column(String(50), nullable=False)
    target_id = Column(BigInteger, nullable=True)
    severity = Column(
        Enum("INFO", "WARNING", "CRITICAL", name="admin_alert_severity_enum"),
        default="WARNING",
    )
    resolved_yn = Column(String(1), default="N")
    resolved_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())  