import httpx

from app.core.config import settings
from app.models.ai import AIProvider


def get_embedding(text: str, provider: AIProvider) -> list[float]:
    if provider.provider_code == "OPENAI":
        return _openai_embedding(text, provider)
    if provider.provider_code == "GEMINI":
        return _gemini_embedding(text, provider)
    if provider.provider_code == "OLLAMA":
        return _ollama_embedding(text, provider)
    raise ValueError(f"지원하지 않는 provider_code입니다: {provider.provider_code}")


def _openai_embedding(text: str, provider: AIProvider) -> list[float]:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
    response = httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
        json={"model": provider.embedding_model, "input": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]


def _gemini_embedding(text: str, provider: AIProvider) -> list[float]:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY가 .env에 설정되어 있지 않습니다.")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{provider.embedding_model}:embedContent?key={settings.gemini_api_key}"
    )
    response = httpx.post(url, json={"content": {"parts": [{"text": text}]}}, timeout=30)
    response.raise_for_status()
    return response.json()["embedding"]["values"]


def _ollama_embedding(text: str, provider: AIProvider) -> list[float]:
    response = httpx.post(
        f"{provider.base_url}/api/embeddings",
        json={"model": provider.embedding_model, "prompt": text},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embedding"]