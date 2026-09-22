from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import CurrentUser, require_role

router = APIRouter(prefix="/api/admin/data", tags=["관리자 원본데이터"])

ADMIN_ONLY = require_role("ADMIN")


def _quote_identifier(name: str) -> str:
    return f"`{name.replace('`', '``')}`"


def _serialize(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    return value


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _serialize(value) for key, value in row.items()}


def _table_names(db: Session) -> list[str]:
    rows = db.execute(
        text(
            """
            SELECT TABLE_NAME AS table_name
            FROM information_schema.tables
            WHERE table_schema = :schema
              AND table_type = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """
        ),
        {"schema": settings.db_name},
    ).all()
    return [str(row[0]) for row in rows]


def _ensure_table(db: Session, table_name: str) -> None:
    if table_name not in set(_table_names(db)):
        raise HTTPException(status_code=404, detail="존재하지 않는 테이블입니다.")


def _columns(db: Session, table_name: str) -> list[dict[str, Any]]:
    _ensure_table(db, table_name)
    rows = db.execute(
        text(
            """
            SELECT
                COLUMN_NAME,
                ORDINAL_POSITION,
                COLUMN_DEFAULT,
                IS_NULLABLE,
                DATA_TYPE,
                COLUMN_TYPE,
                COLUMN_KEY,
                EXTRA
            FROM information_schema.columns
            WHERE table_schema = :schema
              AND table_name = :table_name
            ORDER BY ORDINAL_POSITION
            """
        ),
        {"schema": settings.db_name, "table_name": table_name},
    ).all()

    return [
        {
            "name": str(row[0]),
            "position": row[1],
            "default": _serialize(row[2]),
            "nullable": row[3] == "YES",
            "data_type": row[4],
            "column_type": row[5],
            "primary_key": row[6] == "PRI",
            "auto_increment": "auto_increment" in (row[7] or "").lower(),
            "extra": row[7] or "",
        }
        for row in rows
    ]


def _pk_columns(columns: list[dict[str, Any]]) -> list[str]:
    return [column["name"] for column in columns if column["primary_key"]]


def _validate_payload(
    columns: list[dict[str, Any]],
    payload: dict[str, Any],
    *,
    creating: bool,
) -> dict[str, Any]:
    allowed = {column["name"]: column for column in columns}
    unknown = sorted(set(payload) - set(allowed))
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"존재하지 않는 컬럼입니다: {', '.join(unknown)}",
        )

    cleaned: dict[str, Any] = {}
    for key, value in payload.items():
        column = allowed[key]
        if creating and column["auto_increment"] and value in ("", None):
            continue
        cleaned[key] = value

    if not cleaned:
        raise HTTPException(status_code=400, detail="저장할 값이 없습니다.")
    return cleaned


def _pk_where(
    columns: list[dict[str, Any]],
    pk: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    pk_names = _pk_columns(columns)
    if not pk_names:
        raise HTTPException(
            status_code=400,
            detail="기본키(PK)가 없는 테이블은 안전한 수정/삭제를 지원하지 않습니다.",
        )

    missing = [name for name in pk_names if name not in pk]
    extra = [name for name in pk if name not in pk_names]
    if missing or extra:
        raise HTTPException(
            status_code=400,
            detail=f"PK 값이 올바르지 않습니다. 필요한 PK: {', '.join(pk_names)}",
        )

    params = {f"pk_{index}": pk[name] for index, name in enumerate(pk_names)}
    clause = " AND ".join(
        f"{_quote_identifier(name)} = :pk_{index}"
        for index, name in enumerate(pk_names)
    )
    return clause, params


def _db_error(error: Exception) -> HTTPException:
    message = str(getattr(error, "orig", error))
    lowered = message.lower()

    if "foreign key constraint" in lowered:
        detail = "외래키(FK) 제약 때문에 처리할 수 없습니다. 참조 중인 데이터를 먼저 확인하세요."
    elif "duplicate entry" in lowered:
        detail = "UNIQUE 또는 PRIMARY KEY 값이 중복됩니다."
    elif "cannot be null" in lowered or "doesn't have a default value" in lowered:
        detail = "필수 컬럼 값이 누락되었습니다."
    elif "data truncated" in lowered or "incorrect" in lowered:
        detail = "입력값이 컬럼의 데이터형 또는 ENUM 조건과 맞지 않습니다."
    else:
        detail = f"DB 처리에 실패했습니다: {message[:300]}"

    return HTTPException(status_code=400, detail=detail)


@router.get("/tables")
def list_tables(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(ADMIN_ONLY),
):
    tables = _table_names(db)
    return {"database": settings.db_name, "count": len(tables), "tables": tables}


@router.get("/{table_name}/schema")
def get_table_schema(
    table_name: str,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(ADMIN_ONLY),
):
    columns = _columns(db, table_name)
    return {
        "table": table_name,
        "columns": columns,
        "primary_keys": _pk_columns(columns),
    }


@router.get("/{table_name}/rows")
def list_rows(
    table_name: str,
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(ADMIN_ONLY),
):
    columns = _columns(db, table_name)
    quoted_table = _quote_identifier(table_name)
    pk_names = _pk_columns(columns)
    order_by = (
        " ORDER BY " + ", ".join(_quote_identifier(name) for name in pk_names)
        if pk_names
        else ""
    )
    total = db.execute(text(f"SELECT COUNT(*) FROM {quoted_table}")).scalar_one()
    offset = (page - 1) * size
    rows = db.execute(
        text(f"SELECT * FROM {quoted_table}{order_by} LIMIT :limit OFFSET :offset"),
        {"limit": size, "offset": offset},
    ).mappings().all()

    return {
        "table": table_name,
        "page": page,
        "size": size,
        "total": total,
        "rows": [_serialize_row(dict(row)) for row in rows],
    }


@router.post("/{table_name}/rows")
def create_row(
    table_name: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(ADMIN_ONLY),
):
    columns = _columns(db, table_name)
    values = _validate_payload(columns, payload, creating=True)
    names = list(values)
    quoted_table = _quote_identifier(table_name)
    column_sql = ", ".join(_quote_identifier(name) for name in names)
    value_sql = ", ".join(f":v_{index}" for index in range(len(names)))
    params = {f"v_{index}": values[name] for index, name in enumerate(names)}

    try:
        result = db.execute(
            text(f"INSERT INTO {quoted_table} ({column_sql}) VALUES ({value_sql})"),
            params,
        )
        db.commit()
    except (IntegrityError, SQLAlchemyError) as error:
        db.rollback()
        raise _db_error(error) from error

    return {
        "success": True,
        "message": "행이 생성되었습니다.",
        "inserted_primary_key": _serialize(getattr(result, "lastrowid", None)),
    }


@router.put("/{table_name}/rows")
def update_row(
    table_name: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(ADMIN_ONLY),
):
    pk = payload.get("pk")
    values = payload.get("values")
    if not isinstance(pk, dict) or not isinstance(values, dict):
        raise HTTPException(status_code=400, detail="pk와 values 객체가 필요합니다.")

    columns = _columns(db, table_name)
    values = _validate_payload(columns, values, creating=False)
    where_sql, params = _pk_where(columns, pk)
    set_parts = []
    for index, (name, value) in enumerate(values.items()):
        key = f"value_{index}"
        set_parts.append(f"{_quote_identifier(name)} = :{key}")
        params[key] = value

    quoted_table = _quote_identifier(table_name)
    try:
        result = db.execute(
            text(f"UPDATE {quoted_table} SET {', '.join(set_parts)} WHERE {where_sql}"),
            params,
        )
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="수정할 행을 찾지 못했습니다.")
        db.commit()
    except HTTPException:
        raise
    except (IntegrityError, SQLAlchemyError) as error:
        db.rollback()
        raise _db_error(error) from error

    return {"success": True, "message": "행이 수정되었습니다.", "affected": result.rowcount}


@router.delete("/{table_name}/rows")
def delete_row(
    table_name: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(ADMIN_ONLY),
):
    pk = payload.get("pk")
    if not isinstance(pk, dict):
        raise HTTPException(status_code=400, detail="pk 객체가 필요합니다.")

    columns = _columns(db, table_name)
    where_sql, params = _pk_where(columns, pk)
    quoted_table = _quote_identifier(table_name)

    try:
        result = db.execute(
            text(f"DELETE FROM {quoted_table} WHERE {where_sql}"),
            params,
        )
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="삭제할 행을 찾지 못했습니다.")
        db.commit()
    except HTTPException:
        raise
    except (IntegrityError, SQLAlchemyError) as error:
        db.rollback()
        raise _db_error(error) from error

    return {"success": True, "message": "행이 삭제되었습니다.", "affected": result.rowcount}
