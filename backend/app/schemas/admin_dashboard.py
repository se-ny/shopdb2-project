from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class DashboardOrderItem(BaseModel):
    order_id: int
    order_no: str
    buyer_name: Optional[str] = None
    order_status: str
    total_amount: Decimal
    ordered_at: datetime


class DashboardAlertItem(BaseModel):
    alert_id: int
    alert_code: str
    alert_type: str
    severity: str
    target_table: str
    target_id: Optional[int] = None
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    today_order_count: int
    today_revenue: float
    pending_refund_count: int
    unresolved_alert_count: int
    unresolved_critical_alert_count: int
    recent_orders: List[DashboardOrderItem]
    recent_alerts: List[DashboardAlertItem]