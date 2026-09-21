from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, require_role
from app.schemas.cart import (
    CartItemCreate,
    CartItemQuantityUpdate,
    CartOut,
)
from app.services.cart_service import (
    CartForbiddenError,
    CartNotFoundError,
    CartValidationError,
    add_cart_item_data,
    delete_cart_item_data,
    get_cart_data,
    update_cart_item_data,
)


router = APIRouter(
    prefix="/api/cart",
    tags=["buyer-cart"],
)


buyer_required = require_role("BUYER")


@router.get(
    "",
    response_model=CartOut,
)
def read_cart(
    current_user: CurrentUser = Depends(buyer_required),
) -> dict:
    return get_cart_data(current_user.user_id)


@router.post(
    "/items",
    response_model=CartOut,
    status_code=status.HTTP_201_CREATED,
)
def add_cart_item(
    request: CartItemCreate,
    current_user: CurrentUser = Depends(buyer_required),
) -> dict:
    try:
        return add_cart_item_data(
            buyer_user_id=current_user.user_id,
            variant_id=request.variant_id,
            quantity=request.quantity,
        )
    except CartValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.patch(
    "/items/{cart_item_id}",
    response_model=CartOut,
)
def change_cart_item_quantity(
    cart_item_id: int,
    request: CartItemQuantityUpdate,
    current_user: CurrentUser = Depends(buyer_required),
) -> dict:
    try:
        return update_cart_item_data(
            buyer_user_id=current_user.user_id,
            cart_item_id=cart_item_id,
            quantity=request.quantity,
        )
    except CartNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except CartForbiddenError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    except CartValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete(
    "/items/{cart_item_id}",
    response_model=CartOut,
)
def remove_cart_item(
    cart_item_id: int,
    current_user: CurrentUser = Depends(buyer_required),
) -> dict:
    try:
        return delete_cart_item_data(
            buyer_user_id=current_user.user_id,
            cart_item_id=cart_item_id,
        )
    except CartNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except CartForbiddenError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error