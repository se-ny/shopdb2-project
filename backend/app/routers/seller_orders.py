from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.seller_order import (
    SellerOrderDetailOut,
    SellerOrderItemOut,
    SellerOrderOut,
)


router = APIRouter(
    prefix="/api/seller/orders",
    tags=["판매자 주문관리"],
)


@router.get(
    "",
    response_model=list[SellerOrderOut],
)
def get_seller_orders(
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text(
            """
            SELECT DISTINCT
                o.order_id,
                o.order_no,
                o.buyer_user_id,
                o.org_id,
                o.order_status,
                o.product_amount,
                o.discount_amount,
                o.shipping_amount,
                o.total_amount,
                o.ordered_at
            FROM orders o
            JOIN order_items oi
                ON oi.order_id = o.order_id
            JOIN products p
                ON p.product_id = oi.product_id
            WHERE p.seller_user_id = :seller_user_id
            ORDER BY o.ordered_at DESC,
                     o.order_id DESC
            """
        ),
        {
            "seller_user_id": seller_user_id,
        },
    ).mappings().all()

    return [
        SellerOrderOut(**dict(row))
        for row in rows
    ]


@router.get(
    "/{order_id}",
    response_model=SellerOrderDetailOut,
)
def get_seller_order_detail(
    order_id: int,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    order = db.execute(
        text(
            """
            SELECT DISTINCT
                o.order_id,
                o.order_no,
                o.buyer_user_id,
                o.org_id,
                o.order_status,
                o.product_amount,
                o.discount_amount,
                o.shipping_amount,
                o.total_amount,
                o.ordered_at
            FROM orders o
            JOIN order_items oi
                ON oi.order_id = o.order_id
            JOIN products p
                ON p.product_id = oi.product_id
            WHERE o.order_id = :order_id
              AND p.seller_user_id = :seller_user_id
            """
        ),
        {
            "order_id": order_id,
            "seller_user_id": seller_user_id,
        },
    ).mappings().first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="판매자가 조회할 수 있는 주문을 찾을 수 없습니다.",
        )

    item_rows = db.execute(
        text(
            """
            SELECT
                oi.order_item_id,
                oi.order_id,
                oi.product_id,
                oi.variant_id,
                oi.product_name_snapshot,
                oi.sku_snapshot,
                oi.quantity,
                oi.unit_price,
                oi.item_amount,
                oi.item_status
            FROM order_items oi
            JOIN products p
                ON p.product_id = oi.product_id
            WHERE oi.order_id = :order_id
              AND p.seller_user_id = :seller_user_id
            ORDER BY oi.order_item_id
            """
        ),
        {
            "order_id": order_id,
            "seller_user_id": seller_user_id,
        },
    ).mappings().all()

    items = [
        SellerOrderItemOut(**dict(row))
        for row in item_rows
    ]

    return SellerOrderDetailOut(
        **dict(order),
        items=items,
    )