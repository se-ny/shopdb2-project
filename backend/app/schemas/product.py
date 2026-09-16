from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


ProductStatus = Literal[
    "READY",
    "SALE",
    "SOLD_OUT",
    "STOPPED",
    "DELETED",
]

ImageType = Literal[
    "MAIN",
    "DETAIL",
    "THUMBNAIL",
    "OPTION",
]


class ProductBase(BaseModel):
    seller_user_id: int
    category_id: int

    product_code: str = Field(
        min_length=1,
        max_length=50,
    )

    product_name: str = Field(
        min_length=1,
        max_length=200,
    )

    short_description: Optional[str] = None
    description: Optional[str] = None

    regular_price: Decimal = Field(
        gt=0,
    )

    sale_price: Decimal = Field(
        gt=0,
    )

    product_status: ProductStatus = "READY"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None

    product_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    short_description: Optional[str] = None
    description: Optional[str] = None

    regular_price: Optional[Decimal] = Field(
        default=None,
        gt=0,
    )

    sale_price: Optional[Decimal] = Field(
        default=None,
        gt=0,
    )

    product_status: Optional[ProductStatus] = None


class ProductOut(ProductBase):
    product_id: int

    category_name: Optional[str] = None
    seller_name: Optional[str] = None

    main_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class VariantCreate(BaseModel):
    product_id: int

    sku_code: str = Field(
        min_length=1,
        max_length=100,
    )

    option_name1: Optional[str] = None
    option_value1: Optional[str] = None

    option_name2: Optional[str] = None
    option_value2: Optional[str] = None

    additional_price: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )


class VariantUpdate(BaseModel):
    sku_code: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    option_name1: Optional[str] = None
    option_value1: Optional[str] = None

    option_name2: Optional[str] = None
    option_value2: Optional[str] = None

    additional_price: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    active_yn: Optional[str] = Field(
        default=None,
        pattern="^[YN]$",
    )


class VariantOut(VariantCreate):
    variant_id: int

    active_yn: str = Field(
        default="Y",
        pattern="^[YN]$",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


class InventoryUpdate(BaseModel):
    stock_quantity: Optional[int] = Field(
        default=None,
        ge=0,
    )

    safety_stock: Optional[int] = Field(
        default=None,
        ge=0,
    )


class InventoryOut(BaseModel):
    inventory_id: int
    org_id: int
    org_name: str
    variant_id: int

    stock_quantity: int
    reserved_quantity: int
    safety_stock: int
    available_quantity: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProductImageCreate(BaseModel):
    public_url: str = Field(
        min_length=1,
        max_length=2000,
    )

    thumbnail_url: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    original_file_name: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    image_type: ImageType = "DETAIL"

    alt_text: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    display_order: int = Field(
        default=0,
        ge=0,
    )


class ProductImageUpdate(BaseModel):
    public_url: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=2000,
    )

    thumbnail_url: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    image_type: Optional[ImageType] = None

    alt_text: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    display_order: Optional[int] = Field(
        default=None,
        ge=0,
    )

    active_yn: Optional[str] = Field(
        default=None,
        pattern="^[YN]$",
    )


class ProductImageOut(BaseModel):
    product_image_id: int
    product_id: int
    file_id: int

    public_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    image_type: ImageType

    alt_text: Optional[str] = None
    display_order: int

    active_yn: str = Field(
        default="Y",
        pattern="^[YN]$",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )