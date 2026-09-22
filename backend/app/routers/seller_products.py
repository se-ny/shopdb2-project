from typing import Generator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import engine
from app.schemas.product import (
    InventoryOut,
    InventoryUpdate,
    ProductCreate,
    ProductImageCreate,
    ProductImageOut,
    ProductImageUpdate,
    ProductOut,
    ProductUpdate,
    VariantCreate,
    VariantOut,
    VariantUpdate,
)


router = APIRouter(
    prefix="/api/seller/products",
    tags=["판매자 상품관리"],
)


def get_db() -> Generator[Session, None, None]:
    db = Session(engine)

    try:
        yield db
    finally:
        db.close()


PRODUCT_SELECT = """
SELECT
    p.product_id,
    p.seller_user_id,
    p.category_id,
    p.product_code,
    p.product_name,
    p.short_description,
    p.description,
    p.regular_price,
    p.sale_price,
    p.product_status,
    c.category_name,
    u.user_name AS seller_name,
    f.public_url AS main_image_url,
    f.thumbnail_url
FROM products p
JOIN categories c
    ON p.category_id = c.category_id
JOIN users u
    ON p.seller_user_id = u.user_id
LEFT JOIN product_images pi
    ON p.product_id = pi.product_id
    AND pi.image_type = 'MAIN'
    AND pi.active_yn = 'Y'
LEFT JOIN file_assets f
    ON pi.file_id = f.file_id
"""


def _to_product(row) -> ProductOut:
    return ProductOut(**dict(row._mapping))


def _get_variant(
    variant_id: int,
    db: Session,
):
    return db.execute(
        text(
            """
            SELECT
                variant_id,
                product_id,
                sku_code,
                option_name1,
                option_value1,
                option_name2,
                option_value2,
                additional_price,
                active_yn
            FROM product_variants
            WHERE variant_id = :variant_id
            """
        ),
        {"variant_id": variant_id},
    ).mappings().first()


def _validate_active_seller(
    seller_user_id: int,
    db: Session,
):
    """임시 판매자 권한 검증.

    로그인/JWT 도입 전까지 요청의 seller_user_id를 이용해
    SELLER 역할과 ACTIVE 판매자 상태를 확인한다.
    """
    seller = db.execute(
        text(
            """
            SELECT
                u.user_id,
                sp.seller_status,
                EXISTS (
                    SELECT 1
                    FROM user_roles ur
                    JOIN roles r
                        ON ur.role_id = r.role_id
                    WHERE ur.user_id = u.user_id
                      AND r.role_code = 'SELLER'
                ) AS is_seller
            FROM users u
            LEFT JOIN seller_profiles sp
                ON sp.user_id = u.user_id
            WHERE u.user_id = :seller_user_id
            """
        ),
        {"seller_user_id": seller_user_id},
    ).mappings().first()

    if seller is None:
        raise HTTPException(
            status_code=400,
            detail="존재하지 않는 사용자입니다.",
        )

    if not seller["is_seller"]:
        raise HTTPException(
            status_code=403,
            detail="SELLER 권한이 있는 사용자만 처리할 수 있습니다.",
        )

    if seller["seller_status"] is None:
        raise HTTPException(
            status_code=403,
            detail="판매자 프로필이 등록되어 있지 않습니다.",
        )

    if seller["seller_status"] != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail="ACTIVE 상태의 판매자만 처리할 수 있습니다.",
        )

    return seller


def _require_product_owner(
    product_id: int,
    seller_user_id: int,
    db: Session,
):
    """판매자 자격과 상품 소유권을 함께 확인한다."""
    _validate_active_seller(seller_user_id, db)

    product = db.execute(
        text(
            """
            SELECT
                product_id,
                seller_user_id
            FROM products
            WHERE product_id = :product_id
            """
        ),
        {"product_id": product_id},
    ).mappings().first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다.",
        )

    if product["seller_user_id"] != seller_user_id:
        raise HTTPException(
            status_code=403,
            detail="다른 판매자의 상품은 변경할 수 없습니다.",
        )

    return product


@router.get("", response_model=list[ProductOut])
def get_products(
    keyword: Optional[str] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    seller_user_id: Optional[int] = Query(default=None),
    product_status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    where = ["1 = 1"]

    params = {
        "skip": skip,
        "limit": limit,
    }

    if keyword:
        where.append(
            "(p.product_name LIKE :keyword OR p.product_code LIKE :keyword)"
        )
        params["keyword"] = f"%{keyword}%"

    if category_id is not None:
        where.append("p.category_id = :category_id")
        params["category_id"] = category_id

    if seller_user_id is not None:
        where.append("p.seller_user_id = :seller_user_id")
        params["seller_user_id"] = seller_user_id

    if product_status:
        where.append("p.product_status = :product_status")
        params["product_status"] = product_status

    query = text(
        PRODUCT_SELECT
        + " WHERE "
        + " AND ".join(where)
        + " ORDER BY p.created_at DESC LIMIT :limit OFFSET :skip"
    )

    rows = db.execute(query, params).fetchall()

    return [_to_product(row) for row in rows]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            PRODUCT_SELECT
            + " WHERE p.product_id = :product_id"
        ),
        {"product_id": product_id},
    ).first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다.",
        )

    return _to_product(row)


@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    category_exists = db.execute(
        text(
            """
            SELECT 1
            FROM categories
            WHERE category_id = :category_id
            """
        ),
        {"category_id": payload.category_id},
    ).first()

    if category_exists is None:
        raise HTTPException(
            status_code=400,
            detail="존재하지 않는 카테고리입니다.",
        )

    _validate_active_seller(
        payload.seller_user_id,
        db,
    )

    if payload.sale_price > payload.regular_price:
        raise HTTPException(
            status_code=400,
            detail="판매가는 정상가보다 높을 수 없습니다.",
        )

    try:
        result = db.execute(
            text(
                """
                INSERT INTO products
                (
                    seller_user_id,
                    category_id,
                    product_code,
                    product_name,
                    short_description,
                    description,
                    regular_price,
                    sale_price,
                    product_status
                )
                VALUES
                (
                    :seller_user_id,
                    :category_id,
                    :product_code,
                    :product_name,
                    :short_description,
                    :description,
                    :regular_price,
                    :sale_price,
                    :product_status
                )
                """
            ),
            payload.model_dump(),
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"상품 등록 실패: {exc}",
        ) from exc

    return get_product(result.lastrowid, db)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    current = db.execute(
        text(
            """
            SELECT
                regular_price,
                sale_price
            FROM products
            WHERE product_id = :product_id
            """
        ),
        {"product_id": product_id},
    ).mappings().first()

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다.",
        )

    data = payload.model_dump(exclude_unset=True)

    if "seller_user_id" in data:
        if data["seller_user_id"] != seller_user_id:
            raise HTTPException(
                status_code=403,
                detail="상품 소유 판매자는 변경할 수 없습니다.",
            )
        data.pop("seller_user_id")

    if not data:
        return get_product(product_id, db)

    regular_price = data.get(
        "regular_price",
        current["regular_price"],
    )

    sale_price = data.get(
        "sale_price",
        current["sale_price"],
    )

    if sale_price > regular_price:
        raise HTTPException(
            status_code=400,
            detail="판매가는 정상가보다 높을 수 없습니다.",
        )

    if "category_id" in data:
        exists = db.execute(
            text(
                """
                SELECT 1
                FROM categories
                WHERE category_id = :category_id
                """
            ),
            {"category_id": data["category_id"]},
        ).first()

        if exists is None:
            raise HTTPException(
                status_code=400,
                detail="존재하지 않는 카테고리입니다.",
            )

    fields = []
    params = {
        "product_id": product_id,
    }

    for key, value in data.items():
        fields.append(f"{key} = :{key}")
        params[key] = value

    try:
        db.execute(
            text(
                f"""
                UPDATE products
                SET {", ".join(fields)}
                WHERE product_id = :product_id
                """
            ),
            params,
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"상품 수정 실패: {exc}",
        ) from exc

    return get_product(product_id, db)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    db.execute(
        text(
            """
            UPDATE products
            SET product_status = 'DELETED'
            WHERE product_id = :product_id
            """
        ),
        {"product_id": product_id},
    )

    db.commit()

    return None


@router.get(
    "/{product_id}/variants",
    response_model=list[VariantOut],
)
def get_variants(
    product_id: int,
    db: Session = Depends(get_db),
):
    exists = db.execute(
        text(
            """
            SELECT 1
            FROM products
            WHERE product_id = :product_id
            """
        ),
        {"product_id": product_id},
    ).first()

    if exists is None:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다.",
        )

    rows = db.execute(
        text(
            """
            SELECT
                variant_id,
                product_id,
                sku_code,
                option_name1,
                option_value1,
                option_name2,
                option_value2,
                additional_price,
                active_yn
            FROM product_variants
            WHERE product_id = :product_id
            ORDER BY variant_id
            """
        ),
        {"product_id": product_id},
    ).fetchall()

    return [
        VariantOut(**dict(row._mapping))
        for row in rows
    ]


@router.post(
    "/{product_id}/variants",
    response_model=VariantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_variant(
    product_id: int,
    payload: VariantCreate,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    if payload.product_id != product_id:
        raise HTTPException(
            status_code=400,
            detail="URL의 상품 ID와 요청 상품 ID가 다릅니다.",
        )

    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    try:
        result = db.execute(
            text(
                """
                INSERT INTO product_variants
                (
                    product_id,
                    sku_code,
                    option_name1,
                    option_value1,
                    option_name2,
                    option_value2,
                    additional_price
                )
                VALUES
                (
                    :product_id,
                    :sku_code,
                    :option_name1,
                    :option_value1,
                    :option_name2,
                    :option_value2,
                    :additional_price
                )
                """
            ),
            payload.model_dump(),
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"옵션 등록 실패: {exc}",
        ) from exc

    row = _get_variant(result.lastrowid, db)

    return VariantOut(**dict(row))


@router.put(
    "/{product_id}/variants/{variant_id}",
    response_model=VariantOut,
)
def update_variant(
    product_id: int,
    variant_id: int,
    payload: VariantUpdate,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    current = db.execute(
        text(
            """
            SELECT
                variant_id,
                product_id
            FROM product_variants
            WHERE variant_id = :variant_id
              AND product_id = :product_id
            """
        ),
        {
            "variant_id": variant_id,
            "product_id": product_id,
        },
    ).first()

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="해당 상품의 옵션을 찾을 수 없습니다.",
        )

    data = payload.model_dump(exclude_unset=True)

    if not data:
        row = _get_variant(variant_id, db)

        return VariantOut(**dict(row))

    fields = []
    params = {
        "variant_id": variant_id,
        "product_id": product_id,
    }

    for key, value in data.items():
        fields.append(f"{key} = :{key}")
        params[key] = value

    try:
        db.execute(
            text(
                f"""
                UPDATE product_variants
                SET {", ".join(fields)}
                WHERE variant_id = :variant_id
                  AND product_id = :product_id
                """
            ),
            params,
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"옵션 수정 실패: {exc}",
        ) from exc

    row = _get_variant(variant_id, db)

    return VariantOut(**dict(row))


@router.delete(
    "/{product_id}/variants/{variant_id}",
    response_model=VariantOut,
)
def delete_variant(
    product_id: int,
    variant_id: int,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    current = db.execute(
        text(
            """
            SELECT
                variant_id,
                product_id,
                active_yn
            FROM product_variants
            WHERE variant_id = :variant_id
              AND product_id = :product_id
            """
        ),
        {
            "variant_id": variant_id,
            "product_id": product_id,
        },
    ).first()

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="해당 상품의 옵션을 찾을 수 없습니다.",
        )

    db.execute(
        text(
            """
            UPDATE product_variants
            SET active_yn = 'N'
            WHERE variant_id = :variant_id
              AND product_id = :product_id
            """
        ),
        {
            "variant_id": variant_id,
            "product_id": product_id,
        },
    )

    db.commit()

    row = _get_variant(variant_id, db)

    return VariantOut(**dict(row))


@router.get(
    "/{product_id}/inventory",
    response_model=list[InventoryOut],
)
def get_inventory(
    product_id: int,
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text(
            """
            SELECT
                i.inventory_id,
                i.org_id,
                ou.org_name,
                i.variant_id,
                i.stock_quantity,
                i.reserved_quantity,
                i.safety_stock,
                (
                    i.stock_quantity - i.reserved_quantity
                ) AS available_quantity
            FROM inventories i
            JOIN org_units ou
                ON i.org_id = ou.org_id
            JOIN product_variants pv
                ON i.variant_id = pv.variant_id
            WHERE pv.product_id = :product_id
            ORDER BY
                ou.org_id,
                i.variant_id
            """
        ),
        {"product_id": product_id},
    ).fetchall()

    return [
        InventoryOut(**dict(row._mapping))
        for row in rows
    ]


@router.put(
    "/{product_id}/inventory/{inventory_id}",
    response_model=InventoryOut,
)
def update_inventory(
    product_id: int,
    inventory_id: int,
    payload: InventoryUpdate,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    # 판매자 권한 + 상품 소유권 확인
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    # 변경 전 재고 조회
    current = db.execute(
        text(
            """
            SELECT
                i.inventory_id,
                i.org_id,
                ou.org_name,
                i.variant_id,
                i.stock_quantity,
                i.reserved_quantity,
                i.safety_stock
            FROM inventories i
            JOIN org_units ou
                ON i.org_id = ou.org_id
            JOIN product_variants pv
                ON i.variant_id = pv.variant_id
            WHERE i.inventory_id = :inventory_id
              AND pv.product_id = :product_id
            """
        ),
        {
            "inventory_id": inventory_id,
            "product_id": product_id,
        },
    ).mappings().first()

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="해당 상품의 재고를 찾을 수 없습니다.",
        )

    data = payload.model_dump(exclude_unset=True)

    # 수정할 값이 없으면 현재 재고 그대로 반환
    if not data:
        return InventoryOut(
            **current,
            available_quantity=(
                current["stock_quantity"]
                - current["reserved_quantity"]
            ),
        )

    # 변경 전 값 저장
    stock_before = current["stock_quantity"]
    reserved_before = current["reserved_quantity"]

    # 요청에 없는 값은 기존 값 유지
    stock_after = data.get(
        "stock_quantity",
        stock_before,
    )

    reserved_after = reserved_before

    quantity_change = stock_after - stock_before

    fields = []
    params = {
        "inventory_id": inventory_id,
    }

    for key, value in data.items():
        fields.append(f"{key} = :{key}")
        params[key] = value

    try:
        # 1. 현재 재고 수정
        db.execute(
            text(
                f"""
                UPDATE inventories
                SET {", ".join(fields)}
                WHERE inventory_id = :inventory_id
                """
            ),
            params,
        )

        # 2. 실제 stock_quantity가 변경됐을 때만
        #    재고 변동 내역 생성
        if quantity_change != 0:
            db.execute(
                text(
                    """
                    INSERT INTO inventory_movements
                    (
                        inventory_id,
                        movement_type,
                        quantity_change,
                        stock_before,
                        stock_after,
                        reserved_before,
                        reserved_after,
                        reference_type,
                        reference_id,
                        reason,
                        changed_by_user_id
                    )
                    VALUES
                    (
                        :inventory_id,
                        :movement_type,
                        :quantity_change,
                        :stock_before,
                        :stock_after,
                        :reserved_before,
                        :reserved_after,
                        :reference_type,
                        :reference_id,
                        :reason,
                        :changed_by_user_id
                    )
                    """
                ),
                {
                    "inventory_id": inventory_id,
                    "movement_type": "ADJUST",
                    "quantity_change": quantity_change,
                    "stock_before": stock_before,
                    "stock_after": stock_after,
                    "reserved_before": reserved_before,
                    "reserved_after": reserved_after,
                    "reference_type": "SELLER_MANUAL",
                    "reference_id": None,
                    "reason": "판매자 재고 수동 조정",
                    "changed_by_user_id": seller_user_id,
                },
            )

        # 재고 변경과 변동내역을 동시에 확정
        db.commit()

    except Exception as exc:
        # 하나라도 실패하면 둘 다 취소
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"재고 수정 실패: {exc}",
        ) from exc

    # 수정된 재고 다시 조회
    row = db.execute(
        text(
            """
            SELECT
                i.inventory_id,
                i.org_id,
                ou.org_name,
                i.variant_id,
                i.stock_quantity,
                i.reserved_quantity,
                i.safety_stock,
                (
                    i.stock_quantity - i.reserved_quantity
                ) AS available_quantity
            FROM inventories i
            JOIN org_units ou
                ON i.org_id = ou.org_id
            JOIN product_variants pv
                ON i.variant_id = pv.variant_id
            WHERE i.inventory_id = :inventory_id
              AND pv.product_id = :product_id
            """
        ),
        {
            "inventory_id": inventory_id,
            "product_id": product_id,
        },
    ).mappings().first()

    return InventoryOut(**dict(row))

@router.get(
    "/{product_id}/inventory/{inventory_id}/movements"
)
def get_inventory_movements(
    product_id: int,
    inventory_id: int,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    # 판매자 권한 + 상품 소유권 확인
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    # 해당 재고가 이 상품에 속하는지 확인
    inventory = db.execute(
        text(
            """
            SELECT
                i.inventory_id
            FROM inventories i
            JOIN product_variants pv
                ON i.variant_id = pv.variant_id
            WHERE i.inventory_id = :inventory_id
              AND pv.product_id = :product_id
            """
        ),
        {
            "inventory_id": inventory_id,
            "product_id": product_id,
        },
    ).first()

    if inventory is None:
        raise HTTPException(
            status_code=404,
            detail="해당 상품의 재고를 찾을 수 없습니다.",
        )

    rows = db.execute(
        text(
            """
            SELECT
                movement_id,
                inventory_id,
                movement_type,
                quantity_change,
                stock_before,
                stock_after,
                reserved_before,
                reserved_after,
                reference_type,
                reference_id,
                reason,
                changed_by_user_id,
                created_at
            FROM inventory_movements
            WHERE inventory_id = :inventory_id
            ORDER BY created_at DESC, movement_id DESC
            """
        ),
        {
            "inventory_id": inventory_id,
        },
    ).mappings().all()

    return [dict(row) for row in rows]


@router.get(
    "/{product_id}/images",
    response_model=list[ProductImageOut],
)
def get_product_images(
    product_id: int,
    db: Session = Depends(get_db),
):
    product_exists = db.execute(
        text(
            """
            SELECT 1
            FROM products
            WHERE product_id = :product_id
            """
        ),
        {"product_id": product_id},
    ).first()

    if product_exists is None:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다.",
        )

    rows = db.execute(
        text(
            """
            SELECT
                pi.product_image_id,
                pi.product_id,
                pi.file_id,
                fa.public_url,
                fa.thumbnail_url,
                pi.image_type,
                pi.alt_text,
                pi.display_order,
                pi.active_yn
            FROM product_images pi
            JOIN file_assets fa
                ON pi.file_id = fa.file_id
            WHERE pi.product_id = :product_id
            ORDER BY
                pi.display_order,
                pi.product_image_id
            """
        ),
        {"product_id": product_id},
    ).mappings().all()

    return [
        ProductImageOut(**dict(row))
        for row in rows
    ]


@router.post(
    "/{product_id}/images",
    response_model=ProductImageOut,
    status_code=status.HTTP_201_CREATED,
)
def create_product_image(
    product_id: int,
    payload: ProductImageCreate,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    try:
        file_result = db.execute(
            text(
                """
                INSERT INTO file_assets
                (
                    file_type,
                    storage_type,
                    original_file_name,
                    public_url,
                    thumbnail_url,
                    active_yn
                )
                VALUES
                (
                    'IMAGE',
                    'URL',
                    :original_file_name,
                    :public_url,
                    :thumbnail_url,
                    'Y'
                )
                """
            ),
            {
                "original_file_name":
                    payload.original_file_name,
                "public_url":
                    payload.public_url,
                "thumbnail_url":
                    payload.thumbnail_url,
            },
        )

        file_id = file_result.lastrowid

        if payload.image_type == "MAIN":
            db.execute(
                text(
                    """
                    UPDATE product_images
                    SET active_yn = 'N'
                    WHERE product_id = :product_id
                      AND image_type = 'MAIN'
                    """
                ),
                {"product_id": product_id},
            )

        image_result = db.execute(
            text(
                """
                INSERT INTO product_images
                (
                    product_id,
                    file_id,
                    image_type,
                    alt_text,
                    display_order,
                    active_yn
                )
                VALUES
                (
                    :product_id,
                    :file_id,
                    :image_type,
                    :alt_text,
                    :display_order,
                    'Y'
                )
                """
            ),
            {
                "product_id": product_id,
                "file_id": file_id,
                "image_type":
                    payload.image_type,
                "alt_text":
                    payload.alt_text,
                "display_order":
                    payload.display_order,
            },
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"상품 이미지 등록 실패: {exc}",
        ) from exc

    row = db.execute(
        text(
            """
            SELECT
                pi.product_image_id,
                pi.product_id,
                pi.file_id,
                fa.public_url,
                fa.thumbnail_url,
                pi.image_type,
                pi.alt_text,
                pi.display_order,
                pi.active_yn
            FROM product_images pi
            JOIN file_assets fa
                ON pi.file_id = fa.file_id
            WHERE pi.product_image_id =
                :product_image_id
            """
        ),
        {
            "product_image_id":
                image_result.lastrowid,
        },
    ).mappings().first()

    return ProductImageOut(**dict(row))


@router.put(
    "/{product_id}/images/{product_image_id}",
    response_model=ProductImageOut,
)
def update_product_image(
    product_id: int,
    product_image_id: int,
    payload: ProductImageUpdate,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    current = db.execute(
        text(
            """
            SELECT
                pi.product_image_id,
                pi.file_id
            FROM product_images pi
            WHERE pi.product_image_id =
                :product_image_id
              AND pi.product_id =
                :product_id
            """
        ),
        {
            "product_image_id":
                product_image_id,
            "product_id":
                product_id,
        },
    ).mappings().first()

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="상품 이미지를 찾을 수 없습니다.",
        )

    data = payload.model_dump(
        exclude_unset=True,
    )

    try:
        file_fields = []
        file_params = {
            "file_id": current["file_id"],
        }

        if "public_url" in data:
            file_fields.append(
                "public_url = :public_url"
            )
            file_params["public_url"] = (
                data["public_url"]
            )

        if "thumbnail_url" in data:
            file_fields.append(
                "thumbnail_url = :thumbnail_url"
            )
            file_params["thumbnail_url"] = (
                data["thumbnail_url"]
            )

        if file_fields:
            db.execute(
                text(
                    f"""
                    UPDATE file_assets
                    SET {", ".join(file_fields)}
                    WHERE file_id = :file_id
                    """
                ),
                file_params,
            )

        image_data = {
            key: value
            for key, value in data.items()
            if key
            not in {
                "public_url",
                "thumbnail_url",
            }
        }

        if image_data.get("image_type") == "MAIN":
            db.execute(
                text(
                    """
                    UPDATE product_images
                    SET active_yn = 'N'
                    WHERE product_id = :product_id
                      AND image_type = 'MAIN'
                      AND product_image_id !=
                          :product_image_id
                    """
                ),
                {
                    "product_id": product_id,
                    "product_image_id":
                        product_image_id,
                },
            )

        if image_data:
            fields = []
            params = {
                "product_image_id":
                    product_image_id,
            }

            for key, value in image_data.items():
                fields.append(
                    f"{key} = :{key}"
                )
                params[key] = value

            db.execute(
                text(
                    f"""
                    UPDATE product_images
                    SET {", ".join(fields)}
                    WHERE product_image_id =
                        :product_image_id
                    """
                ),
                params,
            )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"상품 이미지 수정 실패: {exc}",
        ) from exc

    row = db.execute(
        text(
            """
            SELECT
                pi.product_image_id,
                pi.product_id,
                pi.file_id,
                fa.public_url,
                fa.thumbnail_url,
                pi.image_type,
                pi.alt_text,
                pi.display_order,
                pi.active_yn
            FROM product_images pi
            JOIN file_assets fa
                ON pi.file_id = fa.file_id
            WHERE pi.product_image_id =
                :product_image_id
            """
        ),
        {
            "product_image_id":
                product_image_id,
        },
    ).mappings().first()

    return ProductImageOut(**dict(row))


@router.delete(
    "/{product_id}/images/{product_image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product_image(
    product_id: int,
    product_image_id: int,
    seller_user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    _require_product_owner(
        product_id,
        seller_user_id,
        db,
    )

    current = db.execute(
        text(
            """
            SELECT
                product_image_id,
                file_id
            FROM product_images
            WHERE product_image_id =
                :product_image_id
              AND product_id = :product_id
            """
        ),
        {
            "product_image_id":
                product_image_id,
            "product_id":
                product_id,
        },
    ).mappings().first()

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="상품 이미지를 찾을 수 없습니다.",
        )

    try:
        db.execute(
            text(
                """
                UPDATE product_images
                SET active_yn = 'N'
                WHERE product_image_id =
                    :product_image_id
                """
            ),
            {
                "product_image_id":
                    product_image_id,
            },
        )

        db.execute(
            text(
                """
                UPDATE file_assets
                SET active_yn = 'N'
                WHERE file_id = :file_id
                """
            ),
            {
                "file_id":
                    current["file_id"],
            },
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"상품 이미지 삭제 실패: {exc}",
        ) from exc

    return None
