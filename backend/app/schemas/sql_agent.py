from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class SqlAgentQueryRequest(BaseModel):
    question: str
    provider_code: str = "OLLAMA"


class SqlAgentQueryResponse(BaseModel):
    log_id: int
    generated_sql: str
    execution_status: str
    columns: List[str] = []
    rows: List[dict[str, Any]] = []
    result_summary: str
    response_time_ms: int


class SqlAgentLogResponse(BaseModel):
    log_id: int
    log_code: str
    user_id: Optional[int] = None
    question_text: Optional[str] = None
    generated_sql: Optional[str] = None
    execution_status: str
    result_summary: Optional[str] = None
    response_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SqlAgentLogListResponse(BaseModel):
    total: int
    items: List[SqlAgentLogResponse]