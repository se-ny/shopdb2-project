from datetime import datetime
from typing import Optional, List, Literal, Any

from pydantic import BaseModel, ConfigDict

ProviderType = Literal["CLOUD", "LOCAL"]
SourceType = Literal["DATABASE", "FILE", "URL", "API", "MANUAL"]
DocumentStatus = Literal["READY", "PROCESSING", "INDEXED", "ERROR"]


class AIProviderResponse(BaseModel):
    provider_id: int
    provider_code: str
    provider_name: str
    provider_type: ProviderType
    base_url: Optional[str] = None
    chat_model: Optional[str] = None
    embedding_model: Optional[str] = None
    active_yn: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RagDocumentCreate(BaseModel):
    provider_id: Optional[int] = None
    org_id: Optional[int] = None
    document_type: Optional[str] = None
    document_name: str
    source_type: Optional[SourceType] = "MANUAL"
    source_uri: Optional[str] = None
    content_text: str
    version: Optional[str] = None


class RagDocumentResponse(BaseModel):
    document_id: int
    provider_id: Optional[int] = None
    org_id: Optional[int] = None
    document_type: Optional[str] = None
    document_name: str
    source_type: Optional[SourceType] = None
    source_uri: Optional[str] = None
    content_text: Optional[str] = None
    version: Optional[str] = None
    document_status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RagChunkResponse(BaseModel):
    chunk_id: int
    document_id: int
    chunk_no: int
    chunk_text: str
    token_count: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class RagQueryRequest(BaseModel):
    question: str
    provider_code: str = "OPENAI"
    org_id: Optional[int] = None
    top_k: int = 3
    user_id: Optional[int] = None


class RagQueryResponse(BaseModel):
    answer: str
    retrieved_chunks: List[RagChunkResponse]
    response_time_ms: int