from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SourceType = Literal["RAG", "SQL_AGENT"]
FeedbackScore = Literal["GOOD", "BAD"]


class FeedbackCreate(BaseModel):
    source_type: SourceType
    source_log_id: int
    feedback_score: FeedbackScore
    feedback_reason: Optional[str] = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    feedback_id: int
    feedback_code: str
    source_type: SourceType
    source_log_id: int
    user_id: Optional[int] = None
    feedback_score: FeedbackScore
    feedback_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    total: int
    items: List[FeedbackResponse]


class FeedbackStatsBySource(BaseModel):
    GOOD: int = 0
    BAD: int = 0


class FeedbackStatsResponse(BaseModel):
    RAG: FeedbackStatsBySource
    SQL_AGENT: FeedbackStatsBySource