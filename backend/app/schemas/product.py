from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    seller_user_id: int
    category_id: int
    product_code: str = Field(min_length=1, max_length=50)
    product_name: str = Field(min_length=1, max_length=200)
    short_description: Optional[str] = None
    description: Optional[str] = None
    regular_price: Decimal = Field(gt=0)
    sale_price: Decimal = Field(gt=0)
    product_status: str = "READY"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    product_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    short_description: Optional[str] = None
    description: Optional[str] = None
    regular_price: Optional[Decimal] = Field(default=None, gt=0)
    sale_price: Optional[Decimal] = Field(default=None, gt=0)
    product_status: Optional[str] = None


class ProductOut(ProductBase):
    product_id: int
    category_name: Optional[str] = None
    seller_name: Optional[str] = None
    main_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VariantCreate(BaseModel):
    product_id: int
    sku_code: str = Field(min_length=1, max_length=100)
    option_name1: Optional[str] = None
    option_value1: Optional[str] = None
    option_name2: Optional[str] = None
    option_value2: Optional[str] = None
    additional_price: Decimal = Decimal("0")


class VariantOut(VariantCreate):
    variant_id: int
    active_yn: str = "Y"


class InventoryOut(BaseModel):
    inventory_id: int
    org_id: int
    org_name: str
    variant_id: int
    stock_quantity: int
    reserved_quantity: int
    safety_stock: int
    available_quantity: int
