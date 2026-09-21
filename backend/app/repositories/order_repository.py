from sqlalchemy import text

from app.core.database import engine


def get_order_product(product_id: int, variant_id: int) -> dict | None:
    """
    주문할 상품, 옵션, 재고 및 판매 조직 정보를 조회합니다.
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
            pv.additional_price,
            pv.active_yn,

            i.inventory_id,
            i.org_id,
            i.stock_quantity,
            i.reserved_quantity,
            i.safety_stock

        FROM products AS p

        JOIN product_variants AS pv
            ON pv.product_id = p.product_id

        JOIN inventories AS i
            ON i.variant_id = pv.variant_id

        WHERE p.product_id = :product_id
          AND pv.variant_id = :variant_id
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {
                "product_id": product_id,
                "variant_id": variant_id,
            },
        ).mappings().first()

    return dict(row) if row else None


def get_user(user_id: int) -> dict | None:
    """
    주문을 생성하는 구매자가 실제 회원인지 확인합니다.
    """

    query = text(
        """
        SELECT
            user_id,
            user_name,
            user_status
        FROM users
        WHERE user_id = :user_id
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {"user_id": user_id},
        ).mappings().first()

    return dict(row) if row else None


def create_order(
    *,
    order_no: str,
    buyer_user_id: int,
    org_id: int,
    items: list[dict],
    product_amount,
    receiver_name: str,
    receiver_phone: str,
    zipcode: str | None,
    shipping_address1: str,
    shipping_address2: str | None,
) -> int:
    """
    주문, 여러 주문상품, 재고 예약을 하나의 트랜잭션으로 처리합니다.

    하나라도 실패하면 주문 전체를 롤백합니다.
    """

    order_query = text(
        """
        INSERT INTO orders (
            order_no,
            buyer_user_id,
            org_id,
            order_status,
            product_amount,
            discount_amount,
            shipping_amount,
            total_amount,
            receiver_name,
            receiver_phone,
            zipcode,
            shipping_address1,
            shipping_address2
        )
        VALUES (
            :order_no,
            :buyer_user_id,
            :org_id,
            'ORDERED',
            :product_amount,
            0,
            0,
            :total_amount,
            :receiver_name,
            :receiver_phone,
            :zipcode,
            :shipping_address1,
            :shipping_address2
        )
        """
    )

    item_query = text(
        """
        INSERT INTO order_items (
            order_id,
            product_id,
            variant_id,
            product_name_snapshot,
            sku_snapshot,
            quantity,
            unit_price,
            item_amount,
            item_status
        )
        VALUES (
            :order_id,
            :product_id,
            :variant_id,
            :product_name_snapshot,
            :sku_snapshot,
            :quantity,
            :unit_price,
            :item_amount,
            'ORDERED'
        )
        """
    )

    reserve_inventory_query = text(
        """
        UPDATE inventories
        SET reserved_quantity = reserved_quantity + :quantity
        WHERE org_id = :org_id
          AND variant_id = :variant_id
          AND (
                stock_quantity
                - reserved_quantity
                - safety_stock
              ) >= :quantity
        """
    )

    reduce_cart_query = text(
        """
        UPDATE cart_items
        SET quantity = quantity - :quantity
        WHERE cart_item_id = :cart_item_id
          AND quantity > :quantity
        """
    )

    delete_cart_query = text(
        """
        DELETE FROM cart_items
        WHERE cart_item_id = :cart_item_id
          AND quantity = :quantity
        """
    )

    with engine.begin() as connection:
        # 1. 주문 1건 생성
        result = connection.execute(
            order_query,
            {
                "order_no": order_no,
                "buyer_user_id": buyer_user_id,
                "org_id": org_id,
                "product_amount": product_amount,
                "total_amount": product_amount,
                "receiver_name": receiver_name,
                "receiver_phone": receiver_phone,
                "zipcode": zipcode,
                "shipping_address1": shipping_address1,
                "shipping_address2": shipping_address2,
            },
        )

        order_id = result.lastrowid

        # 2. 주문상품을 여러 건 생성하고 각각 재고 예약
        for item in items:
            connection.execute(
                item_query,
                {
                    "order_id": order_id,
                    "product_id": item["product_id"],
                    "variant_id": item["variant_id"],
                    "product_name_snapshot": item["product_name"],
                    "sku_snapshot": item["sku_code"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "item_amount": item["item_amount"],
                },
            )

            inventory_result = connection.execute(
                reserve_inventory_query,
                {
                    "quantity": item["quantity"],
                    "org_id": org_id,
                    "variant_id": item["variant_id"],
                },
            )

            if inventory_result.rowcount != 1:
                raise ValueError(
                    "주문 처리 중 재고가 부족해졌거나 "
                    "재고 정보를 찾을 수 없습니다."
                )
            cart_item_id = item.get("cart_item_id")

            if cart_item_id is not None:
                reduce_result = connection.execute(
                    reduce_cart_query,
                    {
                        "cart_item_id": cart_item_id,
                        "quantity": item["quantity"],
                    },
                )

                if reduce_result.rowcount == 0:
                    delete_result = connection.execute(
                        delete_cart_query,
                        {
                            "cart_item_id": cart_item_id,
                            "quantity": item["quantity"],
                        },
                    )

                    if delete_result.rowcount != 1:
                        raise ValueError(
                            "주문 처리 중 장바구니 수량이 변경되었습니다."
                        )
                    
    return order_id


def get_orders_by_buyer(buyer_user_id: int) -> list[dict]:
    """
    구매자의 주문 목록을 최신 주문부터 조회합니다.
    """

    query = text(
        """
        SELECT
            order_id,
            order_no,
            buyer_user_id,
            org_id,
            order_status,
            product_amount,
            discount_amount,
            shipping_amount,
            total_amount,
            receiver_name,
            receiver_phone,
            zipcode,
            shipping_address1,
            shipping_address2,
            ordered_at
        FROM orders
        WHERE buyer_user_id = :buyer_user_id
        ORDER BY ordered_at DESC, order_id DESC
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"buyer_user_id": buyer_user_id},
        ).mappings().all()

    return [dict(row) for row in rows]


def get_order(order_id: int) -> dict | None:
    """
    주문 정보를 조회합니다.
    """

    query = text(
        """
        SELECT
            order_id,
            order_no,
            buyer_user_id,
            org_id,
            order_status,
            product_amount,
            discount_amount,
            shipping_amount,
            total_amount,
            receiver_name,
            receiver_phone,
            zipcode,
            shipping_address1,
            shipping_address2,
            ordered_at
        FROM orders
        WHERE order_id = :order_id
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {"order_id": order_id},
        ).mappings().first()

    return dict(row) if row else None


def get_order_items(order_id: int) -> list[dict]:
    """
    특정 주문에 포함된 주문상품을 조회합니다.
    """

    query = text(
        """
        SELECT
            order_item_id,
            product_id,
            variant_id,
            product_name_snapshot,
            sku_snapshot,
            quantity,
            unit_price,
            item_amount,
            item_status
        FROM order_items
        WHERE order_id = :order_id
        ORDER BY order_item_id
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"order_id": order_id},
        ).mappings().all()

    return [dict(row) for row in rows]