from sqlalchemy import text

from app.core.database import engine


def get_sale_products() -> list[dict]:
    """판매 중이며 활성 카테고리에 속한 상품 목록과 대표 이미지를 조회합니다."""

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
            c.category_name,

            (
                SELECT fa.public_url
                FROM product_images AS pi
                JOIN file_assets AS fa
                    ON fa.file_id = pi.file_id
                   AND fa.active_yn = 'Y'
                WHERE pi.product_id = p.product_id
                  AND pi.image_type = 'MAIN'
                  AND pi.active_yn = 'Y'
                ORDER BY pi.display_order, pi.product_image_id
                LIMIT 1
            ) AS main_image_url,

            (
                SELECT COALESCE(
                    fa.thumbnail_url,
                    fa.public_url
                )
                FROM product_images AS pi
                JOIN file_assets AS fa
                    ON fa.file_id = pi.file_id
                   AND fa.active_yn = 'Y'
                WHERE pi.product_id = p.product_id
                  AND pi.image_type = 'MAIN'
                  AND pi.active_yn = 'Y'
                ORDER BY pi.display_order, pi.product_image_id
                LIMIT 1
            ) AS thumbnail_url

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

def get_product_detail(product_id: int) -> list[dict]:
    """판매 중인 상품의 상세정보, 옵션, 재고, 대표 이미지를 조회합니다."""

    query = text(
        """
        SELECT
            p.product_id,
            p.product_code,
            p.product_name,
            p.short_description,
            p.description,
            p.regular_price,
            p.sale_price,
            p.product_status,

            c.category_id,
            c.category_name,

            pv.variant_id,
            pv.sku_code,
            pv.option_name1,
            pv.option_value1,
            pv.option_name2,
            pv.option_value2,
            pv.additional_price,

            i.stock_quantity,
            i.reserved_quantity,
            i.safety_stock,
            GREATEST(
                COALESCE(i.stock_quantity, 0) - COALESCE(i.reserved_quantity, 0),
                0
            ) AS available_quantity,


            pi.alt_text,
            fa.public_url,
            fa.thumbnail_url

        FROM products AS p

        JOIN categories AS c
            ON c.category_id = p.category_id

        LEFT JOIN product_variants AS pv
            ON pv.product_id = p.product_id
            AND pv.active_yn = 'Y'

        LEFT JOIN inventories AS i
            ON i.variant_id = pv.variant_id

        LEFT JOIN product_images AS pi
            ON pi.product_id = p.product_id
            AND pi.image_type = 'MAIN'
            AND pi.active_yn = 'Y'

        LEFT JOIN file_assets AS fa
            ON fa.file_id = pi.file_id
            AND fa.active_yn = 'Y'

        WHERE p.product_id = :product_id
          AND p.product_status = 'SALE'
          AND c.active_yn = 'Y'

        ORDER BY pv.variant_id
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"product_id": product_id},
        )

        product_detail = [
            dict(row)
            for row in result.mappings().all()
        ]

    return product_detail