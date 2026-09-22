import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role, CurrentUser
from app.models.ai import AiResponseFeedback, RagQueryLog
from app.schemas.ai_feedback import (
    FeedbackCreate,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackStatsResponse,
)

router = APIRouter(prefix="/api/ai/feedback", tags=["AI 응답 피드백"])


def _generate_feedback_code() -> str:
    return f"FB-{uuid.uuid4().hex[:16].upper()}"


@router.post("", response_model=FeedbackResponse, status_code=201)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    if payload.source_type == "RAG":
        log = db.query(RagQueryLog).filter(
            RagQueryLog.query_log_id == payload.source_log_id
        ).first()
        if not log:
            raise HTTPException(status_code=404, detail="해당 질의 기록을 찾을 수 없습니다.")
        if log.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="본인이 받은 응답에만 피드백을 남길 수 있습니다.")
    # SQL_AGENT는 아직 기능이 없어 로그 검증은 생략합니다.
    # (다음 단계인 자연어 SQL 에이전트를 만들 때 같은 방식으로 검증을 추가하면 됩니다.)

    feedback = AiResponseFeedback(
        feedback_code=_generate_feedback_code(),
        source_type=payload.source_type,
        source_log_id=payload.source_log_id,
        user_id=current_user.user_id,
        feedback_score=payload.feedback_score,
        feedback_reason=payload.feedback_reason,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("", response_model=FeedbackListResponse)
def list_feedback(
    source_type: Optional[str] = Query(default=None),
    feedback_score: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    query = db.query(AiResponseFeedback)
    if source_type:
        query = query.filter(AiResponseFeedback.source_type == source_type)
    if feedback_score:
        query = query.filter(AiResponseFeedback.feedback_score == feedback_score)

    total = query.count()
    rows = (
        query.order_by(AiResponseFeedback.feedback_id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"total": total, "items": rows}


@router.get("/stats", response_model=FeedbackStatsResponse)
def feedback_stats(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    rows = (
        db.query(
            AiResponseFeedback.source_type,
            AiResponseFeedback.feedback_score,
            sa_func.count(AiResponseFeedback.feedback_id),
        )
        .group_by(AiResponseFeedback.source_type, AiResponseFeedback.feedback_score)
        .all()
    )

    stats = {"RAG": {"GOOD": 0, "BAD": 0}, "SQL_AGENT": {"GOOD": 0, "BAD": 0}}
    for source_type, score, count in rows:
        stats.setdefault(source_type, {"GOOD": 0, "BAD": 0})
        stats[source_type][score] = count

    return stats