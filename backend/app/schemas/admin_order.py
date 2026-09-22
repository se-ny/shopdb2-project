from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class AdminOrderListItem(BaseModel):
    order_id: int
    order_no: str
    buyer_user_id: int
    buyer_name: Optional[str] = None
    org_id: int
    org_name: Optional[str] = None
    order_status: str
    total_amount: Decimal
    ordered_at: datetime


class AdminOrderListResponse(BaseModel):
    total: int
    items: List[AdminOrderListItem]


class AdminOrderItem(BaseModel):
    order_item_id: int
    product_id: int
    variant_id: Optional[int] = None
    product_name_snapshot: str
    sku_snapshot: Optional[str] = None
    quantity: int
    unit_price: Decimal
    item_amount: Decimal
    item_status: Optional[str] = None


class AdminOrderDetail(BaseModel):
    order_id: int
    order_no: str
    buyer_user_id: int
    buyer_name: Optional[str] = None
    org_id: int
    order_status: str
    product_amount: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    zipcode: Optional[str] = None
    shipping_address1: Optional[str] = None
    shipping_address2: Optional[str] = None
    ordered_at: datetime
    items: List[AdminOrderItem] = []