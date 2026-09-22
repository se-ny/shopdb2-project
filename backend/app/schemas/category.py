from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    parent_category_id: Optional[int] = None
    category_name: str
    display_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    parent_category_id: Optional[int] = None
    display_order: Optional[int] = None
    active_yn: Optional[Literal["Y", "N"]] = None


class CategoryResponse(CategoryBase):
    category_id: int
    category_level: int
    active_yn: str

    model_config = ConfigDict(from_attributes=True)