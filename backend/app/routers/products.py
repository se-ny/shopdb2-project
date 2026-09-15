from fastapi import APIRouter

from app.services.product_service import get_product_list


router = APIRouter(
    prefix="/api/products",
    tags=["products"],
)


@router.get("")
def read_products() -> list[dict]:
    """구매자에게 판매 중인 상품 목록을 반환합니다."""

    return get_product_list()