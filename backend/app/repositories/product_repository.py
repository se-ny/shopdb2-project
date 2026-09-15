from sqlalchemy import text

from app.core.database import engine


def get_sale_products() -> list[dict]:
    """판매 중이며 활성 카테고리에 속한 상품 목록을 조회합니다."""

    query = text(
        """
        SELECT
            p.product_id,
            p.product_code,
            p.product_name,
            p.short_description,
            p.regular_price,
            p.sale_price,
            p.product_status,
            c.category_id,
            c.category_name
        FROM products AS p
        JOIN categories AS c
            ON c.category_id = p.category_id
        WHERE p.product_status = 'SALE'
          AND c.active_yn = 'Y'
        ORDER BY p.product_id
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query)

        products = [
            dict(row)
            for row in result.mappings().all()
        ]

    return products