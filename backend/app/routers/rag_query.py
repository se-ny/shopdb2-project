import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ai import AIProvider, RagChunk, RagQueryLog
from app.schemas.ai import RagQueryRequest, RagQueryResponse
from app.services.embeddings import get_embedding
from app.services.chat import get_chat_completion
from app.services.vector_store import search as vector_search

router = APIRouter(prefix="/api/ai", tags=["ai-query"])


@router.post("/query", response_model=RagQueryResponse)
def query_rag(payload: RagQueryRequest, db: Session = Depends(get_db)):
    start = time.perf_counter()

    provider = (
        db.query(AIProvider)
        .filter(AIProvider.provider_code == payload.provider_code, AIProvider.active_yn == "Y")
        .first()
    )
    if not provider:
        raise HTTPException(status_code=400, detail="사용할 수 없는 provider입니다.")

    question_vector = get_embedding(payload.question, provider)
    hits = vector_search(question_vector, payload.top_k, org_id=payload.org_id)
    if not hits:
        raise HTTPException(status_code=404, detail="검색된 문서가 없습니다. 먼저 문서를 인덱싱해주세요.")

    chunk_ids = [chunk_id for chunk_id, _ in hits]
    chunks = db.query(RagChunk).filter(RagChunk.chunk_id.in_(chunk_ids)).all()
    chunks_by_id = {c.chunk_id: c for c in chunks}
    ordered_chunks = [chunks_by_id[cid] for cid in chunk_ids if cid in chunks_by_id]

    context = "\n\n".join(c.chunk_text for c in ordered_chunks)
    answer, prompt_tokens, completion_tokens = get_chat_completion(
        payload.question, context, provider
    )

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    db.add(RagQueryLog(
        user_id=payload.user_id,
        provider_id=provider.provider_id,
        question_text=payload.question,
        response_text=answer,
        retrieved_chunk_ids=chunk_ids,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        response_time_ms=elapsed_ms,
    ))
    db.commit()

    return RagQueryResponse(
        answer=answer,
        retrieved_chunks=ordered_chunks,
        response_time_ms=elapsed_ms,
    )


@router.get("/query-logs", tags=["ai-query"])
def list_query_logs(db: Session = Depends(get_db)):
    logs = db.query(RagQueryLog).order_by(RagQueryLog.query_log_id.desc()).limit(50).all()
    return [
        {
            "query_log_id": l.query_log_id,
            "user_id": l.user_id,
            "question_text": l.question_text,
            "response_text": l.response_text,
            "response_time_ms": l.response_time_ms,
            "created_at": l.created_at,
        }
        for l in logs
    ]