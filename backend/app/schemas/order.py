from pydantic import BaseModel, Field


class OrderCreateItem(BaseModel):
    """주문할 상품 옵션과 수량입니다."""

    product_id: int
    variant_id: int
    quantity: int = Field(gt=0)
    cart_item_id: int | None = None
    

class OrderCreate(BaseModel):
    """로그인한 구매자가 주문 생성 시 전달하는 정보입니다."""

    items: list[OrderCreateItem] = Field(min_length=1)

    receiver_name: str
    receiver_phone: str
    zipcode: str | None = None
    shipping_address1: str
    shipping_address2: str | None = None


class OrderItemOut(BaseModel):
    """주문에 포함된 상품 정보입니다."""

    order_item_id: int
    product_id: int
    variant_id: int | None
    product_name_snapshot: str
    sku_snapshot: str | None
    quantity: int
    unit_price: float
    item_amount: float
    item_status: str


class OrderOut(BaseModel):
    """구매자에게 반환하는 주문 정보입니다."""

    order_id: int
    order_no: str
    buyer_user_id: int
    org_id: int
    order_status: str

    product_amount: float
    discount_amount: float
    shipping_amount: float
    total_amount: float

    receiver_name: str | None
    receiver_phone: str | None
    zipcode: str | None
    shipping_address1: str | None
    shipping_address2: str | None

    ordered_at: str | None = None
    items: list[OrderItemOut] = Field(default_factory=list)