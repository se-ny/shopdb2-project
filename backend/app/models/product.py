from sqlalchemy import Column, BigInteger, String, Enum, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(BigInteger, primary_key=True, autoincrement=True)

    seller_user_id = Column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=False,
    )

    category_id = Column(
        BigInteger,
        ForeignKey("categories.category_id"),
        nullable=False,
    )

    product_code = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    product_name = Column(
        String(200),
        nullable=False,
    )

    short_description = Column(
        String(1000),
        nullable=True,
    )

    description = Column(
        LONGTEXT,
        nullable=True,
    )

    regular_price = Column(
        Numeric(15, 2),
        nullable=False,
    )

    sale_price = Column(
        Numeric(15, 2),
        nullable=False,
    )

    product_status = Column(
        Enum(
            "READY",
            "SALE",
            "SOLD_OUT",
            "STOPPED",
            "DELETED",
            name="product_status_enum",
        ),
        default="READY",
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )