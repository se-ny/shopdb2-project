from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.admin_log_service import log_admin_action

router = APIRouter(prefix="/api/admin/categories", tags=["카테고리관리"])


def _category_snapshot(category: Category) -> dict:
    return {
        "category_name": category.category_name,
        "parent_category_id": category.parent_category_id,
        "category_level": category.category_level,
        "display_order": category.display_order,
        "active_yn": category.active_yn,
    }


@router.get("", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    return (
        db.query(Category)
        .order_by(Category.category_level, Category.display_order, Category.category_id)
        .all()
    )


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
    return category


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    category_level = 1
    if payload.parent_category_id:
        parent = db.query(Category).filter(Category.category_id == payload.parent_category_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="상위 카테고리를 찾을 수 없습니다.")
        category_level = parent.category_level + 1

    category = Category(
        parent_category_id=payload.parent_category_id,
        category_name=payload.category_name,
        display_order=payload.display_order,
        category_level=category_level,
    )
    db.add(category)
    db.flush()  # category_id를 로그에 남기기 위해 commit 전에 INSERT 반영

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="CATEGORY_CREATE",
        target_table="categories",
        target_id=category.category_id,
        org_id=None,
        before_value=None,
        after_value=_category_snapshot(category),
    )

    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

    before = _category_snapshot(category)

    update_data = payload.model_dump(exclude_unset=True)

    # 상위 카테고리가 바뀌면 레벨도 다시 계산
    if "parent_category_id" in update_data:
        new_parent_id = update_data["parent_category_id"]
        if new_parent_id == category.category_id:
            raise HTTPException(status_code=400, detail="자기 자신을 상위 카테고리로 지정할 수 없습니다.")
        if new_parent_id:
            parent = db.query(Category).filter(Category.category_id == new_parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="상위 카테고리를 찾을 수 없습니다.")
            category.category_level = parent.category_level + 1
        else:
            category.category_level = 1

    for field, value in update_data.items():
        setattr(category, field, value)

    after = _category_snapshot(category)

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="CATEGORY_UPDATE",
        target_table="categories",
        target_id=category.category_id,
        org_id=None,
        before_value=before,
        after_value=after,
    )

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=CategoryResponse)
def deactivate_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    """실제 삭제 대신 active_yn='N' 처리 (이 카테고리를 쓰는 상품이 있을 수 있어서 하드 삭제하지 않음)."""
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

    before = {"active_yn": category.active_yn}
    category.active_yn = "N"
    after = {"active_yn": category.active_yn}

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="CATEGORY_DEACTIVATE",
        target_table="categories",
        target_id=category.category_id,
        org_id=None,
        before_value=before,
        after_value=after,
    )

    db.commit()
    db.refresh(category)
    return category