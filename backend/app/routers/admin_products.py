from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role, CurrentUser
from app.models.product import Product
from app.models.user import User
from app.schemas.admin_product import AdminProductListResponse
from app.services.admin_log_service import log_admin_action

router = APIRouter(prefix="/api/admin/products", tags=["상품승인관리"])


@router.get("", response_model=AdminProductListResponse)
def list_products(
    product_status: Optional[str] = Query(default="READY"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    query = (
        db.query(Product, User.user_name)
        .join(User, User.user_id == Product.seller_user_id)
    )
    if product_status:
        query = query.filter(Product.product_status == product_status)

    total = query.count()
    rows = (
        query.order_by(Product.product_id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = []
    for product, seller_name in rows:
        items.append({
            "product_id": product.product_id,
            "product_code": product.product_code,
            "product_name": product.product_name,
            "seller_user_id": product.seller_user_id,
            "seller_name": seller_name,
            "category_id": product.category_id,
            "regular_price": product.regular_price,
            "sale_price": product.sale_price,
            "product_status": product.product_status,
            "created_at": product.created_at,
        })

    return {"total": total, "items": items}


@router.patch("/{product_id}/approve")
def approve_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    if product.product_status != "READY":
        raise HTTPException(status_code=400, detail="승인 대기 상태가 아닙니다.")

    before = {"product_status": product.product_status}
    product.product_status = "SALE"
    after = {"product_status": product.product_status}

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="PRODUCT_APPROVE",
        target_table="products",
        target_id=product.product_id,
        org_id=None,
        before_value=before,
        after_value=after,
    )

    db.commit()
    db.refresh(product)
    return {"product_id": product.product_id, "product_status": product.product_status}


@router.patch("/{product_id}/reject")
def reject_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    if product.product_status != "READY":
        raise HTTPException(status_code=400, detail="승인 대기 상태가 아닙니다.")

    before = {"product_status": product.product_status}
    product.product_status = "STOPPED"
    after = {"product_status": product.product_status}

    log_admin_action(
        db,
        admin_user_id=current_user.user_id,
        action_type="PRODUCT_REJECT",
        target_table="products",
        target_id=product.product_id,
        org_id=None,
        before_value=before,
        after_value=after,
    )

    db.commit()
    db.refresh(product)
    return {"product_id": product.product_id, "product_status": product.product_status}