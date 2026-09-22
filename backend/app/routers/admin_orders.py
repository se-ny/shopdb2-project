from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import require_role, CurrentUser
from app.repositories import order_repository
from app.schemas.admin_order import AdminOrderListResponse, AdminOrderDetail

router = APIRouter(prefix="/api/admin/orders", tags=["주문관리"])


@router.get("", response_model=AdminOrderListResponse)
def list_orders(
    order_status: Optional[str] = Query(default=None),
    org_id: Optional[int] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    rows, total = order_repository.list_orders_admin(
        order_status=order_status, org_id=org_id, skip=skip, limit=limit
    )
    return {"total": total, "items": rows}


@router.get("/{order_id}", response_model=AdminOrderDetail)
def get_order_detail(
    order_id: int,
    current_user: CurrentUser = Depends(require_role("ADMIN")),
):
    order = order_repository.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")

    buyer = order_repository.get_user(order["buyer_user_id"])
    order["buyer_name"] = buyer["user_name"] if buyer else None
    order["items"] = order_repository.get_order_items(order_id)

    return order