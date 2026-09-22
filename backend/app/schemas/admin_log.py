from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class AdminActionLogResponse(BaseModel):
    log_id: int
    log_code: str
    admin_user_id: int
    admin_user_name: Optional[str] = None
    org_id: Optional[int] = None
    action_type: str
    target_table: str
    target_id: Optional[int] = None
    before_value: Optional[Any] = None
    after_value: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminActionLogListResponse(BaseModel):
    total: int
    items: List[AdminActionLogResponse]