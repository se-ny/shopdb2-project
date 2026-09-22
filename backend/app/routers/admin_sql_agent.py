import time
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.agents.sql_agent_graph import sql_agent_app
from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.sql_agent_log import SqlAgentQueryLog
from app.schemas.sql_agent import (
    SqlAgentQueryRequest,
    SqlAgentQueryResponse,
    SqlAgentLogListResponse,
)

router = APIRouter(prefix="/api/admin/sql-agent", tags=["자연어 SQL 에이전트"])


def _generate_log_code() -> str:
    return f"SQL-{uuid.uuid4().hex[:16].upper()}"


@router.post("/query", response_model=SqlAgentQueryResponse)
def query_sql_agent(
    payload: SqlAgentQueryRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    start = time.perf_counter()

    result_state = sql_agent_app.invoke({
        "question": payload.question,
        "provider_code": payload.provider_code,
    })

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    log = SqlAgentQueryLog(
        log_code=_generate_log_code(),
        user_id=current_user.user_id,
        question_text=payload.question,
        generated_sql=result_state.get("generated_sql"),
        execution_status=result_state.get("execution_status", "ERROR"),
        result_summary=result_state.get("result_summary"),
        response_time_ms=elapsed_ms,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return SqlAgentQueryResponse(
        log_id=log.log_id,
        generated_sql=result_state.get("generated_sql", ""),
        execution_status=result_state.get("execution_status", "ERROR"),
        columns=result_state.get("columns", []),
        rows=result_state.get("rows", []),
        result_summary=result_state.get("result_summary", ""),
        response_time_ms=elapsed_ms,
    )


@router.get("/logs", response_model=SqlAgentLogListResponse)
def list_sql_agent_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    query = db.query(SqlAgentQueryLog)
    total = query.count()
    rows = (
        query.order_by(SqlAgentQueryLog.log_id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"total": total, "items": rows}