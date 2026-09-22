from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RefundDecisionPayload(BaseModel):
    """환불 승인 시에만 사용. 비워두면 요청 금액 그대로 승인됩니다."""
    approved_amount: Optional[Decimal] = None


class RefundRequestAdminResponse(BaseModel):
    refund_request_id: int
    order_id: int
    buyer_user_id: int
    refund_reason: Optional[str] = None
    requested_amount: Optional[Decimal] = None
    approved_amount: Optional[Decimal] = None
    refund_status: str
    requested_at: datetime
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentAdminListItem(BaseModel):
    payment_id: int
    order_id: int
    order_no: str
    buyer_name: Optional[str] = None
    pg_provider: str
    payment_status: Optional[str] = None
    requested_amount: Decimal
    approved_amount: Optional[Decimal] = None
    cancelled_amount: Optional[Decimal] = None
    balance_amount: Optional[Decimal] = None
    created_at: datetime


class PaymentAdminListResponse(BaseModel):
    total: int
    items: List[PaymentAdminListItem]


class RefundRequestAdminListItem(BaseModel):
    refund_request_id: int
    order_id: int
    order_no: str
    buyer_name: Optional[str] = None
    refund_reason: Optional[str] = None
    requested_amount: Optional[Decimal] = None
    approved_amount: Optional[Decimal] = None
    refund_status: str
    requested_at: datetime
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RefundRequestAdminListResponse(BaseModel):
    total: int
    items: List[RefundRequestAdminListItem]