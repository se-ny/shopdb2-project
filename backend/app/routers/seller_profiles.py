from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.seller_profile import (
    SellerProfileOut,
    SellerProfileUpdate,
)


router = APIRouter(
    prefix="/api/seller/profile",
    tags=["seller-profile"],
)


@router.get(
    "/{user_id}",
    response_model=SellerProfileOut,
)
def get_seller_profile(
    user_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            SELECT
                seller_id,
                user_id,
                company_name,
                business_number,
                representative_name,
                settlement_bank,
                settlement_account,
                seller_status,
                created_at
            FROM seller_profiles
            WHERE user_id = :user_id
            """
        ),
        {
            "user_id": user_id,
        },
    ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="판매자 정보를 찾을 수 없습니다.",
        )

    return SellerProfileOut(**dict(row))


@router.put(
    "/{user_id}",
    response_model=SellerProfileOut,
)
def update_seller_profile(
    user_id: int,
    payload: SellerProfileUpdate,
    db: Session = Depends(get_db),
):
    current = db.execute(
        text(
            """
            SELECT
                seller_id
            FROM seller_profiles
            WHERE user_id = :user_id
            """
        ),
        {
            "user_id": user_id,
        },
    ).first()

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="판매자 정보를 찾을 수 없습니다.",
        )

    data = payload.model_dump(
        exclude_unset=True,
    )

    if not data:
        raise HTTPException(
            status_code=400,
            detail="수정할 판매자 정보가 없습니다.",
        )

    allowed_fields = {
        "company_name",
        "business_number",
        "representative_name",
        "settlement_bank",
        "settlement_account",
        "seller_status",
    }

    update_fields = []
    params = {
        "user_id": user_id,
    }

    for key, value in data.items():
        if key not in allowed_fields:
            continue

        update_fields.append(
            f"{key} = :{key}"
        )

        params[key] = value

    if not update_fields:
        raise HTTPException(
            status_code=400,
            detail="수정 가능한 판매자 정보가 없습니다.",
        )

    try:
        db.execute(
            text(
                f"""
                UPDATE seller_profiles
                SET {", ".join(update_fields)}
                WHERE user_id = :user_id
                """
            ),
            params,
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"판매자 정보 수정 실패: {exc}",
        ) from exc

    row = db.execute(
        text(
            """
            SELECT
                seller_id,
                user_id,
                company_name,
                business_number,
                representative_name,
                settlement_bank,
                settlement_account,
                seller_status,
                created_at
            FROM seller_profiles
            WHERE user_id = :user_id
            """
        ),
        {
            "user_id": user_id,
        },
    ).mappings().first()

    return SellerProfileOut(**dict(row))