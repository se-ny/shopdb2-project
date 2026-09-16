from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SellerOrderItemOut(BaseModel):
    order_item_id: int
    order_id: int

    product_id: int
    variant_id: Optional[int] = None

    product_name_snapshot: str
    sku_snapshot: Optional[str] = None

    quantity: int

    unit_price: Decimal
    item_amount: Decimal

    item_status: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class SellerOrderOut(BaseModel):
    order_id: int
    order_no: str

    buyer_user_id: int
    org_id: int

    order_status: str

    product_amount: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal

    ordered_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class SellerOrderDetailOut(SellerOrderOut):
    items: list[SellerOrderItemOut] = []