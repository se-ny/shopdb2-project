from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ai import AIProvider
from app.schemas.ai import AIProviderResponse

router = APIRouter(prefix="/api/admin/ai/providers", tags=["ai-providers"])


@router.get("", response_model=List[AIProviderResponse])
def list_providers(db: Session = Depends(get_db)):
    return db.query(AIProvider).order_by(AIProvider.provider_id).all()