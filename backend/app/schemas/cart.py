from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    """구매자가 장바구니에 추가할 상품 옵션과 수량입니다."""

    variant_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class CartItemQuantityUpdate(BaseModel):
    """장바구니 상품의 최종 수량입니다."""

    quantity: int = Field(gt=0)


class CartItemOut(BaseModel):
    """구매자에게 보여줄 장바구니 상품 정보입니다."""

    cart_item_id: int
    product_id: int
    variant_id: int
    product_name: str
    sku_code: str

    option_name1: str | None = None
    option_value1: str | None = None
    option_name2: str | None = None
    option_value2: str | None = None

    quantity: int

    unit_price_snapshot: float
    current_unit_price: float
    price_changed: bool

    product_status: str
    variant_active_yn: str

    available_quantity: int
    purchasable: bool
    unavailable_reason: str | None = None


class CartOut(BaseModel):
    """현재 로그인한 구매자의 장바구니입니다."""

    cart_id: int | None = None
    buyer_user_id: int
    items: list[CartItemOut] = []
    total_item_count: int = 0
    total_quantity: int = 0
    current_total_amount: float = 0