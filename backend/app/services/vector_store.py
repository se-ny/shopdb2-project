from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import settings

COLLECTION_NAME = "shopdb2_rag"

_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def ensure_collection(vector_size: int) -> None:
    existing = [c.name for c in _client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        _client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=vector_size, distance=qmodels.Distance.COSINE
            ),
        )


def upsert_chunk_vector(chunk_id: int, document_id: int, org_id: int | None, vector: list[float]) -> None:
    ensure_collection(len(vector))
    _client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            qmodels.PointStruct(
                id=chunk_id,
                vector=vector,
                payload={"document_id": document_id, "org_id": org_id},
            )
        ],
    )


def delete_chunk_vector(chunk_id: int) -> None:
    try:
        _client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=qmodels.PointIdsList(points=[chunk_id]),
        )
    except UnexpectedResponse as error:
        if error.status_code == 404:
            # 컬렉션이 아직 없으면 지울 것도 없으니 그냥 넘어감
            return
        raise


def search(vector: list[float], top_k: int, org_id: int | None = None) -> list[tuple[int, float]]:
    """(chunk_id, score) 리스트 반환."""
    query_filter = None
    if org_id is not None:
        query_filter = qmodels.Filter(
            must=[qmodels.FieldCondition(key="org_id", match=qmodels.MatchValue(value=org_id))]
        )
    response = _client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
        query_filter=query_filter,
    )
    return [(point.id, point.score) for point in response.points]