from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SellerProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    business_number: Optional[str] = Field(
        default=None,
        max_length=30,
    )

    representative_name: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    settlement_bank: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    settlement_account: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    seller_status: Optional[str] = Field(
        default=None,
        max_length=30,
    )


class SellerProfileOut(BaseModel):
    seller_id: int
    user_id: int

    company_name: str

    business_number: Optional[str] = None
    representative_name: Optional[str] = None

    settlement_bank: Optional[str] = None
    settlement_account: Optional[str] = None

    seller_status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )