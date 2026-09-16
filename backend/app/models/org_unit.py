from sqlalchemy import Column, BigInteger, String, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class OrgUnit(Base):
    __tablename__ = "org_units"

    org_id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_org_id = Column(BigInteger, ForeignKey("org_units.org_id"), nullable=True)
    org_code = Column(String(50), unique=True, nullable=False)
    org_name = Column(String(150), nullable=False)
    org_type = Column(
        Enum("HEADQUARTER", "BRANCH", "STORE", "WAREHOUSE", name="org_type_enum"),
        nullable=False,
    )
    business_number = Column(String(30), nullable=True)
    representative_name = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    zipcode = Column(String(20), nullable=True)
    address1 = Column(String(300), nullable=True)
    address2 = Column(String(300), nullable=True)
    active_yn = Column(String(1), default="Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())