from app.repositories.product_repository import get_sale_products


def get_product_list() -> list[dict]:
    """구매자에게 제공할 판매 중 상품 목록을 반환합니다."""

    products = get_sale_products()

    return products