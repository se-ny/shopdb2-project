import httpx

from app.core.config import settings
from app.models.ai import AIProvider

SYSTEM_PROMPT = (
    "너는 쇼핑몰 고객상담 AI야. 아래 참고 문서만 근거로 답변하고, "
    "문서에 없는 내용은 모른다고 답해."
)


def get_chat_completion(question: str, context: str, provider: AIProvider) -> tuple[str, int, int]:
    user_prompt = f"[참고 문서]\n{context}\n\n[질문]\n{question}"

    if provider.provider_code == "OPENAI":
        return _openai_chat(user_prompt, provider)
    if provider.provider_code == "GEMINI":
        return _gemini_chat(user_prompt, provider)
    if provider.provider_code == "OLLAMA":
        return _ollama_chat(user_prompt, provider)
    raise ValueError(f"지원하지 않는 provider_code입니다: {provider.provider_code}")


def _openai_chat(user_prompt: str, provider: AIProvider) -> tuple[str, int, int]:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
        json={
            "model": provider.chat_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    usage = data.get("usage", {})
    return (
        data["choices"][0]["message"]["content"],
        usage.get("prompt_tokens", 0),
        usage.get("completion_tokens", 0),
    )


def _gemini_chat(user_prompt: str, provider: AIProvider) -> tuple[str, int, int]:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY가 .env에 설정되어 있지 않습니다.")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{provider.chat_model}:generateContent?key={settings.gemini_api_key}"
    )
    response = httpx.post(
        url,
        json={"contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\n{user_prompt}"}]}]},
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    usage = data.get("usageMetadata", {})
    return (
        data["candidates"][0]["content"]["parts"][0]["text"],
        usage.get("promptTokenCount", 0),
        usage.get("candidatesTokenCount", 0),
    )


def _ollama_chat(user_prompt: str, provider: AIProvider) -> tuple[str, int, int]:
    response = httpx.post(
        f"{provider.base_url}/api/chat",
        json={
            "model": provider.chat_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return (
        data["message"]["content"],
        data.get("prompt_eval_count", 0),
        data.get("eval_count", 0),
    )