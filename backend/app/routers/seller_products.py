from typing import Generator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import engine
from app.schemas.product import (
    InventoryOut,
    InventoryUpdate,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    VariantCreate,
    VariantOut,
    VariantUpdate,
)


router = APIRouter(
    prefix="/api/seller/products",
    tags=["상품/판매"],
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

    seller_exists = db.execute(
        text(
            """
            SELECT 1
            FROM users
            WHERE user_id = :seller_user_id
            """
        ),
        {"seller_user_id": payload.seller_user_id},
    ).first()

    if seller_exists is None:
        raise HTTPException(
            status_code=400,
            detail="존재하지 않는 판매자입니다.",
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
    db: Session = Depends(get_db),
):
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
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            SELECT product_status
            FROM products
            WHERE product_id = :product_id
            """
        ),
        {"product_id": product_id},
    ).first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다.",
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
    db: Session = Depends(get_db),
):
    if payload.product_id != product_id:
        raise HTTPException(
            status_code=400,
            detail="URL의 상품 ID와 요청 상품 ID가 다릅니다.",
        )

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
    db: Session = Depends(get_db),
):
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
    db: Session = Depends(get_db),
):
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
    db: Session = Depends(get_db),
):
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

    if not data:
        return InventoryOut(
            **current,
            available_quantity=(
                current["stock_quantity"]
                - current["reserved_quantity"]
            ),
        )

    fields = []
    params = {
        "inventory_id": inventory_id,
    }

    for key, value in data.items():
        fields.append(f"{key} = :{key}")
        params[key] = value

    try:
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

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"재고 수정 실패: {exc}",
        ) from exc

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