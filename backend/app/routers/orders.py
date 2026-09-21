from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, require_role
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

buyer_required = require_role("BUYER")


@router.post(
    "",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    request: OrderCreate,
    current_user: CurrentUser = Depends(buyer_required),
) -> dict:
    """로그인한 구매자의 주문을 생성합니다."""

    try:
        return create_order_data(
            request,
            current_user.user_id,
        )
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
    current_user: CurrentUser = Depends(buyer_required),
) -> list[dict]:
    """로그인한 구매자의 주문 목록을 조회합니다."""

    return get_order_list_data(current_user.user_id)


@router.get(
    "/{order_id}",
    response_model=OrderOut,
)
def read_order_detail(
    order_id: int,
    current_user: CurrentUser = Depends(buyer_required),
) -> dict:
    """로그인한 구매자의 주문 상세를 조회합니다."""

    order = get_order_detail_data(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다.",
        )

    if order["buyer_user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 구매자의 주문은 조회할 수 없습니다.",
        )

    return order