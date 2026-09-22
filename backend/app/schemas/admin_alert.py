from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AdminAlertResponse(BaseModel):
    alert_id: int
    alert_code: str
    org_id: Optional[int] = None
    alert_type: str
    target_table: str
    target_id: Optional[int] = None
    severity: str
    resolved_yn: str
    resolved_by: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminAlertListResponse(BaseModel):
    total: int
    items: List[AdminAlertResponse]