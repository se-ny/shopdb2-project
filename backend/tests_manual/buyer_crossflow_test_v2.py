from __future__ import annotations

import html
import json
import traceback
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from app.core.database import engine
from app.schemas.order import OrderCreate, OrderCreateItem
from app.services.order_service import (
    OrderValidationError,
    create_order_data,
)


BUYER_ID = 4
PRODUCT_ID = 1
VARIANT_ID = 1
CART_ITEM_ID = 52
ORG_ID = 1

BASE = Path(__file__).resolve().parent
EVIDENCE = BASE / "evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)

results = []
original = {}
fatal_error = None


def add_result(name, passed, expected, actual):
    result = {
        "name": name,
        "passed": bool(passed),
        "expected": str(expected),
        "actual": str(actual),
    }
    results.append(result)

    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {name}")
    print(f"       expected: {expected}")
    print(f"       actual  : {actual}")


def row(sql, params=None):
    with engine.connect() as conn:
        value = conn.execute(
            text(sql),
            params or {},
        ).mappings().first()

    return dict(value) if value else None


def scalar(sql, params=None):
    with engine.connect() as conn:
        return conn.execute(
            text(sql),
            params or {},
        ).scalar()


def execute(sql, params=None):
    with engine.begin() as conn:
        result = conn.execute(
            text(sql),
            params or {},
        )

    return result.rowcount


def state():
    return {
        "product": row(
            """
            SELECT
                product_id,
                sale_price,
                product_status
            FROM products
            WHERE product_id = :product_id
            """,
            {"product_id": PRODUCT_ID},
        ),

        "variant": row(
            """
            SELECT
                variant_id,
                active_yn
            FROM product_variants
            WHERE variant_id = :variant_id
            """,
            {"variant_id": VARIANT_ID},
        ),

        "inventory": row(
            """
            SELECT
                inventory_id,
                org_id,
                variant_id,
                stock_quantity,
                reserved_quantity,
                safety_stock,
                stock_quantity
                    - reserved_quantity
                    - safety_stock
                    AS available_quantity
            FROM inventories
            WHERE org_id = :org_id
              AND variant_id = :variant_id
            """,
            {
                "org_id": ORG_ID,
                "variant_id": VARIANT_ID,
            },
        ),

        "cart": row(
            """
            SELECT
                ci.cart_item_id,
                ci.cart_id,
                c.buyer_user_id,
                ci.variant_id,
                ci.quantity,
                ci.unit_price_snapshot
            FROM cart_items AS ci
            JOIN carts AS c
                ON c.cart_id = ci.cart_id
            WHERE ci.cart_item_id = :cart_item_id
            """,
            {"cart_item_id": CART_ITEM_ID},
        ),

        "orders_count":
            scalar("SELECT COUNT(*) FROM orders"),

        "order_items_count":
            scalar("SELECT COUNT(*) FROM order_items"),
    }


def make_order_request():
    return OrderCreate(
        items=[
            OrderCreateItem(
                product_id=PRODUCT_ID,
                variant_id=VARIANT_ID,
                quantity=1,
                cart_item_id=CART_ITEM_ID,
            )
        ],
        receiver_name="자동검증 구매자",
        receiver_phone="010-0000-0000",
        zipcode="00000",
        shipping_address1="SHOPDB2 자동검증 주소",
        shipping_address2="실제 주문 생성 금지 검증",
    )


def attempt_order():
    try:
        result = create_order_data(
            make_order_request(),
            BUYER_ID,
        )

        return {
            "rejected": False,
            "error_type": None,
            "message": None,
            "unexpected_result": result,
        }

    except OrderValidationError as error:
        return {
            "rejected": True,
            "error_type": type(error).__name__,
            "message": str(error),
            "unexpected_result": None,
        }


def compare_no_write(prefix, before, after):
    add_result(
        f"{prefix} - orders unchanged",
        before["orders_count"]
        == after["orders_count"],
        before["orders_count"],
        after["orders_count"],
    )

    add_result(
        f"{prefix} - order_items unchanged",
        before["order_items_count"]
        == after["order_items_count"],
        before["order_items_count"],
        after["order_items_count"],
    )

    add_result(
        f"{prefix} - cart quantity unchanged",
        before["cart"]["quantity"]
        == after["cart"]["quantity"],
        before["cart"]["quantity"],
        after["cart"]["quantity"],
    )

    add_result(
        f"{prefix} - stock unchanged",
        before["inventory"]["stock_quantity"]
        == after["inventory"]["stock_quantity"],
        before["inventory"]["stock_quantity"],
        after["inventory"]["stock_quantity"],
    )

    add_result(
        f"{prefix} - reserved unchanged",
        before["inventory"]["reserved_quantity"]
        == after["inventory"]["reserved_quantity"],
        before["inventory"]["reserved_quantity"],
        after["inventory"]["reserved_quantity"],
    )

    add_result(
        f"{prefix} - safety stock unchanged",
        before["inventory"]["safety_stock"]
        == after["inventory"]["safety_stock"],
        before["inventory"]["safety_stock"],
        after["inventory"]["safety_stock"],
    )


def test_stopped():
    print("\n===== V2 TEST 1: STOPPED -> REAL ORDER CALL =====")

    execute(
        """
        UPDATE products
        SET product_status = 'STOPPED'
        WHERE product_id = :product_id
        """,
        {"product_id": PRODUCT_ID},
    )

    before_order = state()

    result = attempt_order()

    after_order = state()

    add_result(
        "STOPPED - create_order_data rejected",
        result["rejected"],
        "OrderValidationError",
        (
            f"{result['error_type']}: {result['message']}"
            if result["rejected"]
            else result["unexpected_result"]
        ),
    )

    add_result(
        "STOPPED - correct rejection reason",
        result["rejected"]
        and "판매 중이 아닙니다" in result["message"],
        "판매 중이 아닙니다",
        result["message"],
    )

    compare_no_write(
        "STOPPED",
        before_order,
        after_order,
    )


def test_variant_inactive():
    print("\n===== V2 TEST 2: ACTIVE_N -> REAL ORDER CALL =====")

    execute(
        """
        UPDATE product_variants
        SET active_yn = 'N'
        WHERE variant_id = :variant_id
        """,
        {"variant_id": VARIANT_ID},
    )

    before_order = state()

    result = attempt_order()

    after_order = state()

    add_result(
        "ACTIVE_N - create_order_data rejected",
        result["rejected"],
        "OrderValidationError",
        (
            f"{result['error_type']}: {result['message']}"
            if result["rejected"]
            else result["unexpected_result"]
        ),
    )

    add_result(
        "ACTIVE_N - correct rejection reason",
        result["rejected"]
        and "사용할 수 없습니다" in result["message"],
        "사용할 수 없습니다",
        result["message"],
    )

    compare_no_write(
        "ACTIVE_N",
        before_order,
        after_order,
    )


def test_inventory_shortage():
    print("\n===== V2 TEST 3: STOCK SHORTAGE -> REAL ORDER CALL =====")

    inv = state()["inventory"]

    temporary_stock = (
        int(inv["reserved_quantity"])
        + int(inv["safety_stock"])
    )

    execute(
        """
        UPDATE inventories
        SET stock_quantity = :stock_quantity
        WHERE org_id = :org_id
          AND variant_id = :variant_id
        """,
        {
            "stock_quantity": temporary_stock,
            "org_id": ORG_ID,
            "variant_id": VARIANT_ID,
        },
    )

    before_order = state()

    add_result(
        "SHORTAGE - test condition available=0",
        int(
            before_order["inventory"]
            ["available_quantity"]
        ) == 0,
        0,
        before_order["inventory"]
        ["available_quantity"],
    )

    result = attempt_order()

    after_order = state()

    add_result(
        "SHORTAGE - create_order_data rejected",
        result["rejected"],
        "OrderValidationError",
        (
            f"{result['error_type']}: {result['message']}"
            if result["rejected"]
            else result["unexpected_result"]
        ),
    )

    add_result(
        "SHORTAGE - correct rejection reason",
        result["rejected"]
        and "재고가 부족합니다" in result["message"],
        "재고가 부족합니다",
        result["message"],
    )

    compare_no_write(
        "SHORTAGE",
        before_order,
        after_order,
    )


def restore():
    if not original:
        return

    print("\n===== V2 RESTORE =====")

    execute(
        """
        UPDATE products
        SET
            sale_price = :sale_price,
            product_status = :product_status
        WHERE product_id = :product_id
        """,
        {
            "sale_price":
                original["product"]["sale_price"],
            "product_status":
                original["product"]["product_status"],
            "product_id": PRODUCT_ID,
        },
    )

    execute(
        """
        UPDATE product_variants
        SET active_yn = :active_yn
        WHERE variant_id = :variant_id
        """,
        {
            "active_yn":
                original["variant"]["active_yn"],
            "variant_id": VARIANT_ID,
        },
    )

    execute(
        """
        UPDATE inventories
        SET
            stock_quantity = :stock_quantity,
            reserved_quantity = :reserved_quantity,
            safety_stock = :safety_stock
        WHERE org_id = :org_id
          AND variant_id = :variant_id
        """,
        {
            "stock_quantity":
                original["inventory"]
                ["stock_quantity"],
            "reserved_quantity":
                original["inventory"]
                ["reserved_quantity"],
            "safety_stock":
                original["inventory"]
                ["safety_stock"],
            "org_id": ORG_ID,
            "variant_id": VARIANT_ID,
        },
    )


def final_restore_check():
    print("\n===== V2 FINAL RESTORE CHECK =====")

    final = state()

    checks = {
        "product_status":
            final["product"]["product_status"]
            == original["product"]["product_status"],

        "sale_price":
            final["product"]["sale_price"]
            == original["product"]["sale_price"],

        "variant_active_yn":
            final["variant"]["active_yn"]
            == original["variant"]["active_yn"],

        "stock_quantity":
            final["inventory"]["stock_quantity"]
            == original["inventory"]["stock_quantity"],

        "reserved_quantity":
            final["inventory"]["reserved_quantity"]
            == original["inventory"]["reserved_quantity"],

        "safety_stock":
            final["inventory"]["safety_stock"]
            == original["inventory"]["safety_stock"],

        "cart_quantity":
            final["cart"]["quantity"]
            == original["cart"]["quantity"],

        "orders_count":
            final["orders_count"]
            == original["orders_count"],

        "order_items_count":
            final["order_items_count"]
            == original["order_items_count"],
    }

    for name, passed in checks.items():
        add_result(
            f"FINAL RESTORE - {name}",
            passed,
            "same as BEFORE",
            "same" if passed else "DIFFERENT",
        )

    return final


def write_reports(final):
    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    pass_count = sum(
        1 for result in results
        if result["passed"]
    )

    fail_count = sum(
        1 for result in results
        if not result["passed"]
    )

    overall = (
        "PASS"
        if fail_count == 0
        and fatal_error is None
        else "FAIL"
    )

    payload = {
        "generated_at": timestamp,

        "test_type":
            "actual create_order_data dynamic validation",

        "target": {
            "buyer_user_id": BUYER_ID,
            "product_id": PRODUCT_ID,
            "variant_id": VARIANT_ID,
            "cart_item_id": CART_ITEM_ID,
            "org_id": ORG_ID,
        },

        "before": original,
        "final": final,
        "results": results,
        "fatal_error": fatal_error,

        "summary": {
            "pass": pass_count,
            "fail": fail_count,
            "overall": overall,
        },
    }

    json_path = (
        EVIDENCE
        / "buyer_crossflow_order_v2_result.json"
    )

    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    result_rows = []

    for result in results:
        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        result_rows.append(
            "<tr>"
            f"<td>{html.escape(status)}</td>"
            f"<td>{html.escape(result['name'])}</td>"
            f"<td>{html.escape(result['expected'])}</td>"
            f"<td>{html.escape(result['actual'])}</td>"
            "</tr>"
        )

    before_json = html.escape(
        json.dumps(
            original,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    final_json = html.escape(
        json.dumps(
            final,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    fatal_html = html.escape(
        fatal_error or "없음"
    )

    document = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>SHOPDB2 구매자 주문 교차검증 V2</title>

<style>
body {{
    font-family:
        Arial,
        "Malgun Gothic",
        sans-serif;
    margin: 36px;
    line-height: 1.5;
}}

h1, h2 {{
    margin-bottom: 8px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 28px;
}}

th, td {{
    border: 1px solid #999;
    padding: 8px;
    text-align: left;
    vertical-align: top;
}}

.summary {{
    border: 2px solid #333;
    padding: 14px;
    font-size: 20px;
    font-weight: bold;
}}

pre {{
    border: 1px solid #bbb;
    padding: 12px;
    white-space: pre-wrap;
}}
</style>
</head>

<body>

<h1>SHOPDB2 구매자 주문 교차검증 V2</h1>

<p>생성시각: {html.escape(timestamp)}</p>

<p>
실제 호출:
create_order_data(
OrderCreate,
buyer_user_id={BUYER_ID}
)
</p>

<div class="summary">
OVERALL: {overall}<br>
PASS: {pass_count}<br>
FAIL: {fail_count}
</div>

<h2>1. 실제 주문 차단 검증 결과</h2>

<table>
<thead>
<tr>
<th>결과</th>
<th>검증 항목</th>
<th>기대값</th>
<th>실제값</th>
</tr>
</thead>

<tbody>
{''.join(result_rows)}
</tbody>
</table>

<h2>2. 테스트 시작 전 DB</h2>
<pre>{before_json}</pre>

<h2>3. 최종 원복 DB</h2>
<pre>{final_json}</pre>

<h2>4. 치명적 오류</h2>
<pre>{fatal_html}</pre>

<h2>5. 검증 의미</h2>

<p>
판매중지, 옵션 비활성, 재고부족 상태에서
실제 주문 서비스 create_order_data()를 호출하여
OrderValidationError 차단 여부를 검증했습니다.
</p>

<p>
각 실패 시 orders, order_items, Cart 수량,
재고 수량 및 예약수량이 변경되지 않는지도
함께 검증했습니다.
</p>

<h2>6. 보안</h2>

<p>
Access Token, Authorization Bearer,
DB 비밀번호는 이 보고서에 기록하지 않습니다.
</p>

</body>
</html>
"""

    html_path = (
        EVIDENCE
        / "buyer_crossflow_order_v2_report.html"
    )

    html_path.write_text(
        document,
        encoding="utf-8",
    )

    print("\n===== V2 REPORT =====")
    print("JSON :", json_path)
    print("HTML :", html_path)
    print(
        f"PASS={pass_count} "
        f"FAIL={fail_count}"
    )
    print("OVERALL =", overall)


def main():
    global original
    global fatal_error

    print(
        "SHOPDB2 BUYER CROSS-FLOW "
        "ORDER TEST V2"
    )
    print("=" * 48)

    original = state()

    print("\n===== V2 BEFORE =====")
    print(
        json.dumps(
            original,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    # 테스트 시작 전 안전조건
    if original["product"] is None:
        raise RuntimeError(
            "product_id=1이 없습니다."
        )

    if original["variant"] is None:
        raise RuntimeError(
            "variant_id=1이 없습니다."
        )

    if original["inventory"] is None:
        raise RuntimeError(
            "org_id=1 / variant_id=1 "
            "재고가 없습니다."
        )

    if original["cart"] is None:
        raise RuntimeError(
            "cart_item_id=52가 없습니다."
        )

    if (
        int(original["cart"]["buyer_user_id"])
        != BUYER_ID
    ):
        raise RuntimeError(
            "Cart #52 소유자가 buyer 4가 아닙니다."
        )

    if (
        int(original["cart"]["variant_id"])
        != VARIANT_ID
    ):
        raise RuntimeError(
            "Cart #52 variant가 1이 아닙니다."
        )

    if (
        int(original["cart"]["quantity"])
        < 1
    ):
        raise RuntimeError(
            "Cart #52 수량이 1 미만입니다."
        )

    if (
        original["product"]["product_status"]
        != "SALE"
    ):
        raise RuntimeError(
            "시작 전 product_status가 "
            "SALE이 아닙니다."
        )

    if (
        original["variant"]["active_yn"]
        != "Y"
    ):
        raise RuntimeError(
            "시작 전 active_yn이 Y가 아닙니다."
        )

    final = None

    try:
        # TEST 1
        test_stopped()

        # TEST 2를 위해 product만 원복
        execute(
            """
            UPDATE products
            SET product_status = :status
            WHERE product_id = :product_id
            """,
            {
                "status":
                    original["product"]
                    ["product_status"],
                "product_id": PRODUCT_ID,
            },
        )

        test_variant_inactive()

        # TEST 3을 위해 variant 원복
        execute(
            """
            UPDATE product_variants
            SET active_yn = :active_yn
            WHERE variant_id = :variant_id
            """,
            {
                "active_yn":
                    original["variant"]
                    ["active_yn"],
                "variant_id": VARIANT_ID,
            },
        )

        test_inventory_shortage()

    except Exception:
        fatal_error = traceback.format_exc()

        print("\n===== V2 FATAL =====")
        print(fatal_error)

    finally:
        try:
            restore()
            final = final_restore_check()

        except Exception:
            restore_error = traceback.format_exc()

            fatal_error = (
                (fatal_error or "")
                + "\nRESTORE ERROR:\n"
                + restore_error
            )

            print("\n===== RESTORE ERROR =====")
            print(restore_error)

        write_reports(final)


if __name__ == "__main__":
    main()
