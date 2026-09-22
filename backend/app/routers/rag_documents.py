from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.ai import AIProvider, RagDocument, RagChunk, RagEmbedding
from app.schemas.ai import RagDocumentCreate, RagDocumentUpdate, RagDocumentResponse, RagChunkResponse
from app.services.chunking import split_into_chunks
from app.services.embeddings import get_embedding
from app.services.vector_store import upsert_chunk_vector, delete_chunk_vector, COLLECTION_NAME

router = APIRouter(prefix="/api/admin/ai/documents", tags=["AI 문서관리"])


def _delete_document_chunks(document_id: int, db: Session):
    """문서에 딸린 청크/임베딩/Qdrant 벡터를 전부 정리하는 공용 함수."""
    old_chunks = db.query(RagChunk).filter(RagChunk.document_id == document_id).all()
    for c in old_chunks:
        delete_chunk_vector(c.chunk_id)
        db.query(RagEmbedding).filter(RagEmbedding.chunk_id == c.chunk_id).delete()
        db.delete(c)
    db.commit()


@router.get("", response_model=List[RagDocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    return db.query(RagDocument).order_by(RagDocument.document_id).all()


@router.post("", response_model=RagDocumentResponse, status_code=201)
def create_document(
    payload: RagDocumentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    document = RagDocument(**payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.put("/{document_id}", response_model=RagDocumentResponse)
def update_document(
    document_id: int,
    payload: RagDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    document = db.query(RagDocument).filter(RagDocument.document_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    # 원문 내용이 바뀌면 기존 인덱싱은 더 이상 최신 내용을 반영하지 못하므로
    # 상태를 READY로 되돌리고, 기존 청크/임베딩은 정리한다 (재인덱싱은 관리자가 버튼으로 실행)
    if "content_text" in update_data:
        _delete_document_chunks(document_id, db)
        document.document_status = "READY"

    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    document = db.query(RagDocument).filter(RagDocument.document_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    _delete_document_chunks(document_id, db)
    db.delete(document)
    db.commit()


@router.get("/{document_id}/chunks", response_model=List[RagChunkResponse])
def list_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    return (
        db.query(RagChunk)
        .filter(RagChunk.document_id == document_id)
        .order_by(RagChunk.chunk_no)
        .all()
    )


@router.post("/{document_id}/index", response_model=List[RagChunkResponse])
def index_document(
    document_id: int,
    provider_code: str | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    """문서를 청크로 나누고 임베딩을 생성해 Qdrant + MySQL에 저장합니다."""

    document = db.query(RagDocument).filter(RagDocument.document_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    if not document.content_text:
        raise HTTPException(status_code=400, detail="content_text가 비어 있습니다.")

    provider = None
    if provider_code:
        provider = db.query(AIProvider).filter(AIProvider.provider_code == provider_code).first()
    elif document.provider_id:
        provider = db.query(AIProvider).filter(AIProvider.provider_id == document.provider_id).first()
    if not provider:
        provider = db.query(AIProvider).filter(AIProvider.active_yn == "Y").first()
    if not provider:
        raise HTTPException(status_code=400, detail="사용 가능한 AI provider가 없습니다.")

    document.document_status = "PROCESSING"
    db.commit()

    _delete_document_chunks(document_id, db)

    texts = split_into_chunks(document.content_text)
    created_chunks = []

    try:
        for i, text in enumerate(texts, start=1):
            chunk = RagChunk(
                document_id=document_id,
                chunk_no=i,
                chunk_text=text,
                token_count=len(text) // 4,
            )
            db.add(chunk)
            db.flush()  # chunk_id 확보

            vector = get_embedding(text, provider)
            upsert_chunk_vector(chunk.chunk_id, document_id, document.org_id, vector)

            db.add(RagEmbedding(
                chunk_id=chunk.chunk_id,
                embedding_provider=provider.provider_code,
                embedding_model=provider.embedding_model,
                embedding_dimension=len(vector),
                embedding_json=None,  # 실제 벡터는 Qdrant에 저장
                vector_db_type="QDRANT",
                vector_collection=COLLECTION_NAME,
                vector_external_id=str(chunk.chunk_id),
            ))
            created_chunks.append(chunk)

        document.document_status = "INDEXED"
        db.commit()
    except Exception as error:
        db.rollback()
        document.document_status = "ERROR"
        db.commit()
        raise HTTPException(status_code=500, detail=f"인덱싱 실패: {error}") from error

    for c in created_chunks:
        db.refresh(c)
    return created_chunks