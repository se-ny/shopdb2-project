from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict


OrgType = Literal["HEADQUARTER", "BRANCH", "STORE", "WAREHOUSE"]


class OrgUnitBase(BaseModel):
    org_code: str
    org_name: str
    org_type: OrgType
    parent_org_id: Optional[int] = None
    business_number: Optional[str] = None
    representative_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    zipcode: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None


class OrgUnitCreate(OrgUnitBase):
    pass


class OrgUnitUpdate(BaseModel):
    org_name: Optional[str] = None
    org_type: Optional[OrgType] = None
    parent_org_id: Optional[int] = None
    business_number: Optional[str] = None
    representative_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    zipcode: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    active_yn: Optional[Literal["Y", "N"]] = None


class OrgUnitResponse(OrgUnitBase):
    org_id: int
    active_yn: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)