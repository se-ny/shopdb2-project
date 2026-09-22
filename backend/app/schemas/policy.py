from datetime import date, datetime
from typing import Optional, Literal, Any

from pydantic import BaseModel, ConfigDict

ShippingFeePayer = Literal["BUYER", "SELLER", "COMPANY"]


# ---------- 회사정책(이용약관 등) ----------

class CompanyPolicyBase(BaseModel):
    org_id: Optional[int] = None
    policy_code: str
    policy_name: str
    policy_version: str
    policy_type: Optional[str] = None
    policy_content: Optional[str] = None
    effective_from: date
    effective_to: Optional[date] = None


class CompanyPolicyCreate(CompanyPolicyBase):
    pass


class CompanyPolicyUpdate(BaseModel):
    policy_name: Optional[str] = None
    policy_version: Optional[str] = None
    policy_type: Optional[str] = None
    policy_content: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class CompanyPolicyResponse(CompanyPolicyBase):
    policy_id: int
    active_yn: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- 환불정책 ----------

class RefundPolicyBase(BaseModel):
    org_id: Optional[int] = None
    policy_name: str
    allowed_days: int
    unopened_refund_yn: Literal["Y", "N"] = "Y"
    opened_refund_yn: Literal["Y", "N"] = "N"
    defective_refund_yn: Literal["Y", "N"] = "Y"
    shipping_fee_payer: ShippingFeePayer = "BUYER"
    refund_policy_text: Optional[str] = None
    policy_json: Optional[dict[str, Any]] = None
    effective_from: date
    effective_to: Optional[date] = None


class RefundPolicyCreate(RefundPolicyBase):
    pass


class RefundPolicyUpdate(BaseModel):
    policy_name: Optional[str] = None
    allowed_days: Optional[int] = None
    unopened_refund_yn: Optional[Literal["Y", "N"]] = None
    opened_refund_yn: Optional[Literal["Y", "N"]] = None
    defective_refund_yn: Optional[Literal["Y", "N"]] = None
    shipping_fee_payer: Optional[ShippingFeePayer] = None
    refund_policy_text: Optional[str] = None
    policy_json: Optional[dict[str, Any]] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class RefundPolicyResponse(RefundPolicyBase):
    refund_policy_id: int
    active_yn: str

    model_config = ConfigDict(from_attributes=True)