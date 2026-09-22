from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.ai import AIProvider
from app.schemas.ai import AIProviderResponse, AIProviderCreate, AIProviderUpdate

router = APIRouter(prefix="/api/admin/ai/providers", tags=["AI 서비스관리"])


@router.get("", response_model=List[AIProviderResponse])
def list_providers(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    return db.query(AIProvider).order_by(AIProvider.provider_id).all()


@router.post("", response_model=AIProviderResponse, status_code=201)
def create_provider(
    payload: AIProviderCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    provider = AIProvider(**payload.model_dump())
    db.add(provider)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 존재하는 provider_code입니다.")
    db.refresh(provider)
    return provider


@router.put("/{provider_id}", response_model=AIProviderResponse)
def update_provider(
    provider_id: int,
    payload: AIProviderUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    provider = db.query(AIProvider).filter(AIProvider.provider_id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="provider를 찾을 수 없습니다.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(provider, field, value)

    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/{provider_id}", response_model=AIProviderResponse)
def deactivate_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    """실제 삭제 대신 active_yn='N' 처리 (rag_documents, rag_query_logs가 FK로 참조 중)."""
    provider = db.query(AIProvider).filter(AIProvider.provider_id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="provider를 찾을 수 없습니다.")

    provider.active_yn = "N"
    db.commit()
    db.refresh(provider)
    return provider