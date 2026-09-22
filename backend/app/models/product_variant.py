from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric

from app.core.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    variant_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    product_id = Column(
        BigInteger,
        ForeignKey("products.product_id"),
        nullable=False,
    )

    sku_code = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    option_name1 = Column(
        String(100),
        nullable=True,
    )

    option_value1 = Column(
        String(100),
        nullable=True,
    )

    option_name2 = Column(
        String(100),
        nullable=True,
    )

    option_value2 = Column(
        String(100),
        nullable=True,
    )

    additional_price = Column(
        Numeric(15, 2),
        default=0,
    )

    active_yn = Column(
        String(1),
        default="Y",
    )