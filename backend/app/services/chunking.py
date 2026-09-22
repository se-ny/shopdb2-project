def split_into_chunks(text: str, max_chars: int = 500, overlap: int = 50) -> list[str]:
    """단순 길이 기준 청킹. overlap만큼 겹쳐서 문맥 유실을 줄인다."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks