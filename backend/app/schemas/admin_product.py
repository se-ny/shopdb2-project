from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AdminProductListItem(BaseModel):
    product_id: int
    product_code: str
    product_name: str
    seller_user_id: int
    seller_name: Optional[str] = None
    category_id: int
    regular_price: Decimal
    sale_price: Decimal
    product_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminProductListResponse(BaseModel):
    total: int
    items: List[AdminProductListItem]