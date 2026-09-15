from app.repositories.product_repository import (
    get_product_detail,
    get_sale_products,
)


def get_product_list() -> list[dict]:
    """구매자에게 제공할 판매 중 상품 목록을 반환합니다."""

    products = get_sale_products()

    return products

def get_product_detail_data(product_id: int) -> dict | None:
    """상품 상세 조회 결과를 상품 1개와 옵션 목록 구조로 변환합니다."""

    rows = get_product_detail(product_id)

    if not rows:
        return None

    first = rows[0]

    product = {
        "product_id": first["product_id"],
        "product_code": first["product_code"],
        "product_name": first["product_name"],
        "short_description": first["short_description"],
        "description": first["description"],
        "regular_price": first["regular_price"],
        "sale_price": first["sale_price"],
        "product_status": first["product_status"],
        "category": {
            "category_id": first["category_id"],
            "category_name": first["category_name"],
        },
        "image": {
            "alt_text": first["alt_text"],
            "public_url": first["public_url"],
            "thumbnail_url": first["thumbnail_url"],
        },
        "variants": [],
    }

    for row in rows:
        if row["variant_id"] is None:
            continue

        product["variants"].append(
            {
                "variant_id": row["variant_id"],
                "sku_code": row["sku_code"],
                "option_name1": row["option_name1"],
                "option_value1": row["option_value1"],
                "option_name2": row["option_name2"],
                "option_value2": row["option_value2"],
                "additional_price": row["additional_price"],
                "stock_quantity": row["stock_quantity"],
                "reserved_quantity": row["reserved_quantity"],
                "safety_stock": row["safety_stock"],
            }
        )

    return product