from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import (
    OrderValidationError,
    create_order_data,
    get_order_detail_data,
    get_order_list_data,
)


router = APIRouter(
    prefix="/api/orders",
    tags=["구매자 주문관리"],
)


@router.post(
    "",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_order(request: OrderCreate) -> dict:
    """구매자의 주문을 생성합니다."""

    try:
        return create_order_data(request)
    except OrderValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[OrderOut],
)
def read_orders(
    buyer_user_id: int = Query(
        ...,
        gt=0,
        description="주문 목록을 조회할 구매자 사용자 ID",
    ),
) -> list[dict]:
    """구매자별 주문 목록을 조회합니다."""

    return get_order_list_data(buyer_user_id)


@router.get(
    "/{order_id}",
    response_model=OrderOut,
)
def read_order_detail(order_id: int) -> dict:
    """주문 상세와 주문 상품을 조회합니다."""

    order = get_order_detail_data(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다.",
        )

    return order
