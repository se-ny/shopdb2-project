from sqlalchemy import (
    Column, BigInteger, String, Text, JSON, Integer, DateTime, Enum, ForeignKey,
)
from sqlalchemy.sql import func

from app.core.database import Base


class AIProvider(Base):
    __tablename__ = "ai_providers"

    provider_id = Column(BigInteger, primary_key=True, autoincrement=True)
    provider_code = Column(String(50), unique=True, nullable=False)
    provider_name = Column(String(100), nullable=False)
    provider_type = Column(Enum("CLOUD", "LOCAL", name="provider_type_enum"), nullable=False)
    base_url = Column(String(1000), nullable=True)
    chat_model = Column(String(200), nullable=True)
    embedding_model = Column(String(200), nullable=True)
    active_yn = Column(String(1), default="Y")
    created_at = Column(DateTime, server_default=func.now())


class RagDocument(Base):
    __tablename__ = "rag_documents"

    document_id = Column(BigInteger, primary_key=True, autoincrement=True)
    provider_id = Column(BigInteger, ForeignKey("ai_providers.provider_id"), nullable=True)
    org_id = Column(BigInteger, ForeignKey("org_units.org_id"), nullable=True)
    document_type = Column(String(50), nullable=True)
    document_name = Column(String(255), nullable=False)
    source_type = Column(
        Enum("DATABASE", "FILE", "URL", "API", "MANUAL", name="source_type_enum"),
        nullable=True,
    )
    source_uri = Column(String(2000), nullable=True)
    content_text = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)
    document_status = Column(
        Enum("READY", "PROCESSING", "INDEXED", "ERROR", name="document_status_enum"),
        default="READY",
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RagChunk(Base):
    __tablename__ = "rag_chunks"

    chunk_id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_id = Column(BigInteger, ForeignKey("rag_documents.document_id"), nullable=False)
    chunk_no = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class RagEmbedding(Base):
    __tablename__ = "rag_embeddings"

    embedding_id = Column(BigInteger, primary_key=True, autoincrement=True)
    chunk_id = Column(BigInteger, ForeignKey("rag_chunks.chunk_id"), nullable=False)
    embedding_provider = Column(String(50), nullable=True)
    embedding_model = Column(String(200), nullable=True)
    embedding_dimension = Column(Integer, nullable=True)
    embedding_json = Column(JSON, nullable=True)  # Qdrant 사용 시 NULL 유지
    vector_db_type = Column(String(50), nullable=True)
    vector_collection = Column(String(200), nullable=True)
    vector_external_id = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class RagQueryLog(Base):
    __tablename__ = "rag_query_logs"

    query_log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    provider_id = Column(BigInteger, ForeignKey("ai_providers.provider_id"), nullable=True)
    question_text = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    retrieved_chunk_ids = Column(JSON, nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class AiResponseFeedback(Base):
    __tablename__ = "ai_response_feedback"

    feedback_id = Column(BigInteger, primary_key=True, autoincrement=True)
    feedback_code = Column(String(50), unique=True, nullable=False)
    source_type = Column(Enum("RAG", "SQL_AGENT", name="feedback_source_type_enum"), nullable=False)
    source_log_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    feedback_score = Column(Enum("GOOD", "BAD", name="feedback_score_enum"), nullable=False)
    feedback_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())