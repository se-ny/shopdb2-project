import re

from sqlalchemy import text

from app.core.database import engine, SessionLocal
from app.models.ai import AIProvider
from app.services.chat import get_chat_completion


SCHEMA_CONTEXT = """
[사용 가능한 테이블]
- users(user_id, user_name, email, user_type)
- org_units(org_id, org_name, org_type)
- orders(order_id, order_no, buyer_user_id, org_id, order_status, total_amount, ordered_at)
- order_items(order_item_id, order_id, variant_id, quantity, unit_price)
- products(product_id, product_name, category_id, seller_user_id)
- product_variants(variant_id, product_id, sku_code, sale_price)
- inventories(inventory_id, org_id, variant_id, stock_quantity, reserved_quantity, safety_stock)
- payments(payment_id, order_id, payment_status, requested_amount, approved_amount, created_at)
- refund_requests(refund_request_id, order_id, buyer_user_id, refund_status, requested_amount, requested_at)
"""

SQL_SYSTEM_PROMPT = (
    "너는 쇼핑몰 데이터베이스(MySQL)를 조회하는 SQL 생성 도우미야. "
    "아래 스키마에 있는 테이블/컬럼만 사용해서, 사용자의 질문에 답하는 "
    "읽기 전용 SELECT 쿼리 하나만 생성해. "
    "설명이나 마크다운 없이 SQL 쿼리 텍스트만 출력해. "
    "세미콜론으로 여러 문장을 만들지 말고, 반드시 SELECT로 시작하는 단일 쿼리만 작성해.\n"
    + SCHEMA_CONTEXT
)

ALLOWED_TABLES = {
    "users", "org_units", "orders", "order_items", "products",
    "product_variants", "inventories", "payments", "refund_requests",
}

FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter", "truncate",
    "create", "replace", "grant", "revoke", "exec", "execute",
    "call", "into outfile", "load_file",
]

MAX_ROWS = 100


def _get_active_provider(db, provider_code: str) -> AIProvider:
    provider = (
        db.query(AIProvider)
        .filter(AIProvider.provider_code == provider_code, AIProvider.active_yn == "Y")
        .first()
    )
    if not provider:
        raise ValueError(f"사용할 수 없는 provider입니다: {provider_code}")
    return provider


def _strip_code_fence(raw: str) -> str:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```sql\s*|^```\s*|```$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE).strip()
    return cleaned


def generate_sql(question: str, provider_code: str) -> str:
    db = SessionLocal()
    try:
        provider = _get_active_provider(db, provider_code)
        raw_sql, _, _ = get_chat_completion(question, "", provider, system_prompt=SQL_SYSTEM_PROMPT)
        return _strip_code_fence(raw_sql)
    finally:
        db.close()


def validate_sql(sql: str) -> tuple[bool, str]:
    """(통과여부, 통과하면 정제된 SQL / 실패하면 사유)를 반환합니다."""
    cleaned = sql.strip().rstrip(";").strip()

    if not cleaned:
        return False, "생성된 SQL이 비어 있습니다."

    if ";" in cleaned:
        return False, "세미콜론으로 구분된 다중 쿼리는 허용되지 않습니다."

    lowered = cleaned.lower()

    if not lowered.startswith("select"):
        return False, "SELECT 쿼리만 실행할 수 있습니다."

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", lowered):
            return False, f"허용되지 않은 키워드가 포함되어 있습니다: {keyword}"

    referenced_tables = set(re.findall(r"(?:from|join)\s+`?(\w+)`?", lowered))
    unknown_tables = referenced_tables - ALLOWED_TABLES
    if unknown_tables:
        return False, f"허용되지 않은 테이블이 포함되어 있습니다: {', '.join(unknown_tables)}"

    if "limit" not in lowered:
        cleaned = f"{cleaned} LIMIT {MAX_ROWS}"

    return True, cleaned


def execute_readonly_sql(sql: str):
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(row) for row in result.mappings().all()]
    return columns, rows


def summarize_result(question: str, rows: list[dict], provider_code: str) -> str:
    db = SessionLocal()
    try:
        provider = _get_active_provider(db, provider_code)
        preview = rows[:20]
        prompt = f"[질문]\n{question}\n\n[조회 결과 (최대 20건 표시)]\n{preview}"
        summary_text, _, _ = get_chat_completion(
            prompt,
            "",
            provider,
            system_prompt=(
                "너는 SQL 조회 결과를 한국어로 짧게 요약해서 설명해주는 도우미야. "
                "숫자와 핵심 특징 위주로 2~3문장으로 답해."
            ),
        )
        return summary_text
    except Exception:
        return f"조회 결과 {len(rows)}건입니다. (요약 생성 실패)"
    finally:
        db.close()