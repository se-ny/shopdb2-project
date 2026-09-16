from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.repositories.order_repository import (
    create_order,
    get_order,
    get_order_items,
    get_order_product,
    get_orders_by_buyer,
    get_user,
)
from app.schemas.order import OrderCreate


class OrderValidationError(Exception):
    """주문 업무 규칙 검증 실패 시 사용합니다."""


def _generate_order_no() -> str:
    """중복 가능성을 낮춘 주문번호를 생성합니다."""

    date_text = datetime.now().strftime("%Y%m%d")
    random_text = uuid4().hex[:8].upper()

    return f"ORD-{date_text}-{random_text}"


def _serialize_order(order: dict) -> dict:
    """DB 조회 결과를 API 응답용 데이터로 변환합니다."""

    result = dict(order)

    if result.get("ordered_at") is not None:
        result["ordered_at"] = result["ordered_at"].isoformat()

    for key in (
        "product_amount",
        "discount_amount",
        "shipping_amount",
        "total_amount",
    ):
        if result.get(key) is not None:
            result[key] = float(result[key])

    return result


def _serialize_item(item: dict) -> dict:
    """주문상품의 Decimal 값을 JSON 반환 가능한 값으로 변환합니다."""

    result = dict(item)

    if result.get("unit_price") is not None:
        result["unit_price"] = float(result["unit_price"])

    if result.get("item_amount") is not None:
        result["item_amount"] = float(result["item_amount"])

    return result


def create_order_data(request: OrderCreate) -> dict:
    """주문 생성 업무 로직입니다."""

    buyer = get_user(request.buyer_user_id)

    if buyer is None:
        raise OrderValidationError("존재하지 않는 구매자입니다.")

    if buyer["user_status"] != "ACTIVE":
        raise OrderValidationError("현재 주문할 수 없는 사용자입니다.")

    product = get_order_product(
        request.product_id,
        request.variant_id,
    )

    if product is None:
        raise OrderValidationError(
            "상품 또는 선택한 상품 옵션을 찾을 수 없습니다."
        )

    if product["product_status"] != "SALE":
        raise OrderValidationError("현재 판매 중인 상품이 아닙니다.")

    if product["active_yn"] != "Y":
        raise OrderValidationError("현재 사용할 수 없는 상품 옵션입니다.")

    stock_quantity = int(product["stock_quantity"])
    reserved_quantity = int(product["reserved_quantity"])
    safety_stock = int(product["safety_stock"])

    available_quantity = (
        stock_quantity
        - reserved_quantity
        - safety_stock
    )

    if request.quantity > available_quantity:
        raise OrderValidationError(
            f"주문 가능한 재고가 부족합니다. "
            f"현재 주문 가능 수량: {available_quantity}"
        )

    sale_price = Decimal(product["sale_price"])
    additional_price = Decimal(product["additional_price"] or 0)

    unit_price = sale_price + additional_price
    item_amount = unit_price * request.quantity

    order_no = _generate_order_no()

    order_id = create_order(
        order_no=order_no,
        buyer_user_id=request.buyer_user_id,
        org_id=product["org_id"],
        product_id=request.product_id,
        variant_id=request.variant_id,
        product_name=product["product_name"],
        sku_code=product["sku_code"],
        quantity=request.quantity,
        unit_price=unit_price,
        item_amount=item_amount,
        receiver_name=request.receiver_name,
        receiver_phone=request.receiver_phone,
        zipcode=request.zipcode,
        shipping_address1=request.shipping_address1,
        shipping_address2=request.shipping_address2,
    )

    return get_order_detail_data(order_id)


def get_order_list_data(buyer_user_id: int) -> list[dict]:
    """구매자의 주문 목록을 반환합니다."""

    orders = get_orders_by_buyer(buyer_user_id)

    return [_serialize_order(order) for order in orders]


def get_order_detail_data(order_id: int) -> dict | None:
    """주문 상세와 주문상품을 함께 반환합니다."""

    order = get_order(order_id)

    if order is None:
        return None

    result = _serialize_order(order)

    items = get_order_items(order_id)

    result["items"] = [
        _serialize_item(item)
        for item in items
    ]

    return result