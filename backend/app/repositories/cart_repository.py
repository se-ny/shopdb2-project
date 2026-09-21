from decimal import Decimal

from sqlalchemy import text

from app.core.database import engine


def get_cart_by_buyer(buyer_user_id: int) -> dict | None:
    query = text(
        """
        SELECT
            cart_id,
            buyer_user_id,
            created_at,
            updated_at
        FROM carts
        WHERE buyer_user_id = :buyer_user_id
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {"buyer_user_id": buyer_user_id},
        ).mappings().first()

    return dict(row) if row else None


def get_or_create_cart(buyer_user_id: int) -> int:
    """
    구매자의 현재 장바구니를 반환합니다.
    장바구니가 없으면 최초 상품 추가 시 생성합니다.
    """

    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                SELECT cart_id
                FROM carts
                WHERE buyer_user_id = :buyer_user_id
                """
            ),
            {"buyer_user_id": buyer_user_id},
        ).mappings().first()

        if row:
            return int(row["cart_id"])

        result = connection.execute(
            text(
                """
                INSERT INTO carts (buyer_user_id)
                VALUES (:buyer_user_id)
                """
            ),
            {"buyer_user_id": buyer_user_id},
        )

        return int(result.lastrowid)


def get_variant_for_cart(variant_id: int) -> dict | None:
    """
    장바구니 추가/변경에 필요한 현재 상품·옵션·재고 정보를 조회합니다.
    """

    query = text(
        """
        SELECT
            p.product_id,
            p.product_name,
            p.sale_price,
            p.product_status,

            pv.variant_id,
            pv.sku_code,
            pv.option_name1,
            pv.option_value1,
            pv.option_name2,
            pv.option_value2,
            pv.additional_price,
            pv.active_yn,

            COALESCE(i.stock_quantity, 0) AS stock_quantity,
            COALESCE(i.reserved_quantity, 0) AS reserved_quantity,
            COALESCE(i.safety_stock, 0) AS safety_stock

        FROM product_variants AS pv

        JOIN products AS p
            ON p.product_id = pv.product_id

        LEFT JOIN inventories AS i
            ON i.variant_id = pv.variant_id

        WHERE pv.variant_id = :variant_id
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {"variant_id": variant_id},
        ).mappings().first()

    return dict(row) if row else None


def get_cart_items(cart_id: int) -> list[dict]:
    query = text(
        """
        SELECT
            ci.cart_item_id,
            ci.cart_id,
            ci.variant_id,
            ci.quantity,
            ci.unit_price_snapshot,

            p.product_id,
            p.product_name,
            p.sale_price,
            p.product_status,

            pv.sku_code,
            pv.option_name1,
            pv.option_value1,
            pv.option_name2,
            pv.option_value2,
            pv.additional_price,
            pv.active_yn,

            COALESCE(i.stock_quantity, 0) AS stock_quantity,
            COALESCE(i.reserved_quantity, 0) AS reserved_quantity,
            COALESCE(i.safety_stock, 0) AS safety_stock

        FROM cart_items AS ci

        JOIN product_variants AS pv
            ON pv.variant_id = ci.variant_id

        JOIN products AS p
            ON p.product_id = pv.product_id

        LEFT JOIN inventories AS i
            ON i.variant_id = pv.variant_id

        WHERE ci.cart_id = :cart_id

        ORDER BY ci.created_at, ci.cart_item_id
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"cart_id": cart_id},
        ).mappings().all()

    return [dict(row) for row in rows]


def get_cart_item(cart_item_id: int) -> dict | None:
    query = text(
        """
        SELECT
            ci.cart_item_id,
            ci.cart_id,
            ci.variant_id,
            ci.quantity,
            c.buyer_user_id
        FROM cart_items AS ci
        JOIN carts AS c
            ON c.cart_id = ci.cart_id
        WHERE ci.cart_item_id = :cart_item_id
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {"cart_item_id": cart_item_id},
        ).mappings().first()

    return dict(row) if row else None


def add_or_increase_cart_item(
    *,
    cart_id: int,
    variant_id: int,
    quantity: int,
    unit_price_snapshot: Decimal,
) -> None:
    """
    같은 장바구니에 같은 variant가 있으면 수량을 증가시키고,
    없으면 새 항목을 생성합니다.

    재추가 시 snapshot은 현재 가격으로 갱신합니다.
    """

    query = text(
        """
        INSERT INTO cart_items (
            cart_id,
            variant_id,
            quantity,
            unit_price_snapshot
        )
        VALUES (
            :cart_id,
            :variant_id,
            :quantity,
            :unit_price_snapshot
        )
        ON DUPLICATE KEY UPDATE
            quantity = quantity + VALUES(quantity),
            unit_price_snapshot = VALUES(unit_price_snapshot)
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "cart_id": cart_id,
                "variant_id": variant_id,
                "quantity": quantity,
                "unit_price_snapshot": unit_price_snapshot,
            },
        )


def update_cart_item_quantity(
    cart_item_id: int,
    quantity: int,
) -> None:
    query = text(
        """
        UPDATE cart_items
        SET quantity = :quantity
        WHERE cart_item_id = :cart_item_id
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "cart_item_id": cart_item_id,
                "quantity": quantity,
            },
        )


def delete_cart_item(cart_item_id: int) -> None:
    query = text(
        """
        DELETE FROM cart_items
        WHERE cart_item_id = :cart_item_id
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {"cart_item_id": cart_item_id},
        )