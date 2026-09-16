from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class Inventory(Base):
    __tablename__ = "inventories"

    inventory_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    org_id = Column(
        BigInteger,
        ForeignKey("org_units.org_id"),
        nullable=False,
    )

    variant_id = Column(
        BigInteger,
        ForeignKey("product_variants.variant_id"),
        nullable=False,
    )

    stock_quantity = Column(
        Integer,
        nullable=False,
        default=0,
    )

    reserved_quantity = Column(
        Integer,
        nullable=False,
        default=0,
    )

    safety_stock = Column(
        Integer,
        nullable=False,
        default=0,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "org_id",
            "variant_id",
            name="uk_inventory_org_variant",
        ),
    )