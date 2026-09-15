from fastapi import APIRouter, HTTPException

from app.services.product_service import (
    get_product_detail_data,
    get_product_list,
)


router = APIRouter(
    prefix="/api/products",
    tags=["products"],
)


@router.get("")
def read_products() -> list[dict]:
    """구매자에게 판매 중인 상품 목록을 반환합니다."""

    return get_product_list()


@router.get("/{product_id}")
def read_product_detail(product_id: int) -> dict:
    """판매 중인 상품의 상세정보와 옵션, 재고를 반환합니다."""

    product = get_product_detail_data(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다.",
        )

    return product