from decimal import Decimal

from app.repositories.cart_repository import (
    add_or_increase_cart_item,
    delete_cart_item,
    get_cart_by_buyer,
    get_cart_item,
    get_cart_items,
    get_or_create_cart,
    get_variant_for_cart,
    update_cart_item_quantity,
)


class CartValidationError(Exception):
    """장바구니 업무규칙 검증 실패에 사용합니다."""


class CartNotFoundError(Exception):
    """장바구니 상품을 찾을 수 없을 때 사용합니다."""


class CartForbiddenError(Exception):
    """다른 구매자의 장바구니 접근을 차단할 때 사용합니다."""


def _current_unit_price(row: dict) -> Decimal:
    return Decimal(row["sale_price"]) + Decimal(
        row["additional_price"] or 0
    )


def _available_quantity(row: dict) -> int:
    return max(
        0,
        int(row["stock_quantity"])
        - int(row["reserved_quantity"])
        - int(row["safety_stock"]),
    )


def _validate_variant_for_cart(
    variant: dict | None,
    quantity: int,
) -> tuple[Decimal, int]:
    if variant is None:
        raise CartValidationError(
            "선택한 상품 옵션을 찾을 수 없습니다."
        )

    if variant["product_status"] != "SALE":
        raise CartValidationError(
            "현재 판매 중인 상품이 아닙니다."
        )

    if variant["active_yn"] != "Y":
        raise CartValidationError(
            "현재 사용할 수 없는 상품 옵션입니다."
        )

    available_quantity = _available_quantity(variant)

    if quantity > available_quantity:
        raise CartValidationError(
            f"구매 가능한 재고가 부족합니다. "
            f"현재 구매 가능 수량: {available_quantity}"
        )

    return _current_unit_price(variant), available_quantity


def _serialize_cart_item(row: dict) -> dict:
    current_price = _current_unit_price(row)
    snapshot_price = Decimal(row["unit_price_snapshot"])
    available_quantity = _available_quantity(row)

    unavailable_reason = None

    if row["product_status"] != "SALE":
        unavailable_reason = "현재 판매 중인 상품이 아닙니다."
    elif row["active_yn"] != "Y":
        unavailable_reason = "현재 사용할 수 없는 상품 옵션입니다."
    elif available_quantity <= 0:
        unavailable_reason = "현재 구매 가능한 재고가 없습니다."
    elif int(row["quantity"]) > available_quantity:
        unavailable_reason = (
            f"현재 구매 가능 수량은 "
            f"{available_quantity}개입니다."
        )

    return {
        "cart_item_id": row["cart_item_id"],
        "product_id": row["product_id"],
        "variant_id": row["variant_id"],
        "product_name": row["product_name"],
        "sku_code": row["sku_code"],

        "option_name1": row["option_name1"],
        "option_value1": row["option_value1"],
        "option_name2": row["option_name2"],
        "option_value2": row["option_value2"],

        "quantity": row["quantity"],

        "unit_price_snapshot": float(snapshot_price),
        "current_unit_price": float(current_price),
        "price_changed": snapshot_price != current_price,

        "product_status": row["product_status"],
        "variant_active_yn": row["active_yn"],

        "available_quantity": available_quantity,
        "purchasable": unavailable_reason is None,
        "unavailable_reason": unavailable_reason,
    }


def get_cart_data(buyer_user_id: int) -> dict:
    cart = get_cart_by_buyer(buyer_user_id)

    if cart is None:
        return {
            "cart_id": None,
            "buyer_user_id": buyer_user_id,
            "items": [],
            "total_item_count": 0,
            "total_quantity": 0,
            "current_total_amount": 0,
        }

    rows = get_cart_items(cart["cart_id"])
    items = [_serialize_cart_item(row) for row in rows]

    return {
        "cart_id": cart["cart_id"],
        "buyer_user_id": buyer_user_id,
        "items": items,
        "total_item_count": len(items),
        "total_quantity": sum(
            int(item["quantity"])
            for item in items
        ),
        "current_total_amount": sum(
            item["current_unit_price"] * item["quantity"]
            for item in items
        ),
    }


def add_cart_item_data(
    *,
    buyer_user_id: int,
    variant_id: int,
    quantity: int,
) -> dict:
    variant = get_variant_for_cart(variant_id)

    current_price, _ = _validate_variant_for_cart(
        variant,
        quantity,
    )

    cart_id = get_or_create_cart(buyer_user_id)

    # 기존 수량까지 포함했을 때 재고를 넘는지 다시 검사합니다.
    existing_rows = get_cart_items(cart_id)
    existing_quantity = 0

    for row in existing_rows:
        if int(row["variant_id"]) == variant_id:
            existing_quantity = int(row["quantity"])
            break

    total_quantity = existing_quantity + quantity

    _validate_variant_for_cart(
        variant,
        total_quantity,
    )

    add_or_increase_cart_item(
        cart_id=cart_id,
        variant_id=variant_id,
        quantity=quantity,
        unit_price_snapshot=current_price,
    )

    return get_cart_data(buyer_user_id)


def update_cart_item_data(
    *,
    buyer_user_id: int,
    cart_item_id: int,
    quantity: int,
) -> dict:
    cart_item = get_cart_item(cart_item_id)

    if cart_item is None:
        raise CartNotFoundError(
            "장바구니 상품을 찾을 수 없습니다."
        )

    if int(cart_item["buyer_user_id"]) != buyer_user_id:
        raise CartForbiddenError(
            "다른 구매자의 장바구니 상품은 변경할 수 없습니다."
        )

    variant = get_variant_for_cart(
        int(cart_item["variant_id"])
    )

    _validate_variant_for_cart(
        variant,
        quantity,
    )

    update_cart_item_quantity(
        cart_item_id,
        quantity,
    )

    return get_cart_data(buyer_user_id)


def delete_cart_item_data(
    *,
    buyer_user_id: int,
    cart_item_id: int,
) -> dict:
    cart_item = get_cart_item(cart_item_id)

    if cart_item is None:
        raise CartNotFoundError(
            "장바구니 상품을 찾을 수 없습니다."
        )

    if int(cart_item["buyer_user_id"]) != buyer_user_id:
        raise CartForbiddenError(
            "다른 구매자의 장바구니 상품은 삭제할 수 없습니다."
        )

    delete_cart_item(cart_item_id)

    return get_cart_data(buyer_user_id)