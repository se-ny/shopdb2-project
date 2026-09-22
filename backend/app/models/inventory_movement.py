from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    movement_id = Column(BigInteger, primary_key=True, autoincrement=True)

    inventory_id = Column(
        BigInteger,
        ForeignKey("inventories.inventory_id"),
        nullable=False,
        index=True,
    )

    movement_type = Column(
        String(20),
        nullable=False,
    )

    quantity_change = Column(
        Integer,
        nullable=False,
    )

    stock_before = Column(
        Integer,
        nullable=False,
    )

    stock_after = Column(
        Integer,
        nullable=False,
    )

    reserved_before = Column(
        Integer,
        nullable=False,
        default=0,
    )

    reserved_after = Column(
        Integer,
        nullable=False,
        default=0,
    )

    reference_type = Column(
        String(50),
        nullable=True,
    )

    reference_id = Column(
        BigInteger,
        nullable=True,
    )

    reason = Column(
        String(500),
        nullable=True,
    )

    changed_by_user_id = Column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )