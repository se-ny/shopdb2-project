from __future__ import annotations

import html
import json
import re
import traceback
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from app.core.database import engine
from app.services.cart_service import get_cart_data


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


def add_result(name, passed, expected, actual, note=""):
    results.append({
        "name": name,
        "passed": bool(passed),
        "expected": str(expected),
        "actual": str(actual),
        "note": str(note),
    })

    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {name}")
    print(f"       expected: {expected}")
    print(f"       actual  : {actual}")


def scalar(sql, params=None):
    with engine.connect() as conn:
        return conn.execute(
            text(sql), params or {}
        ).scalar()


def row(sql, params=None):
    with engine.connect() as conn:
        value = conn.execute(
            text(sql), params or {}
        ).mappings().first()
    return dict(value) if value else None


def execute(sql, params=None):
    with engine.begin() as conn:
        result = conn.execute(
            text(sql), params or {}
        )
    return result.rowcount


def db_state():
    return {
        "product": row(
            """
            SELECT product_id, sale_price, product_status
            FROM products
            WHERE product_id = :product_id
            """,
            {"product_id": PRODUCT_ID},
        ),
        "variant": row(
            """
            SELECT variant_id, active_yn
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
                  - safety_stock AS available_quantity
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
            SELECT cart_item_id, quantity, unit_price_snapshot
            FROM cart_items
            WHERE cart_item_id = :cart_item_id
            """,
            {"cart_item_id": CART_ITEM_ID},
        ),
        "orders_count": scalar(
            "SELECT COUNT(*) FROM orders"
        ),
        "order_items_count": scalar(
            "SELECT COUNT(*) FROM order_items"
        ),
    }


def cart_target():
    data = get_cart_data(BUYER_ID)

    for item in data["items"]:
        if int(item["cart_item_id"]) == CART_ITEM_ID:
            return item

    return None


def inspect_order_service_source():
    source_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "services"
        / "order_service.py"
    )

    source = source_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    checks = {
        "product_status SALE validation":
            'product["product_status"] != "SALE"' in source,

        "variant active Y validation":
            'product["active_yn"] != "Y"' in source,

        "available quantity calculation":
            all(token in source for token in (
                'product["stock_quantity"]',
                'product["reserved_quantity"]',
                'product["safety_stock"]',
            )),

        "inventory shortage rejection":
            "available_quantity" in source
            and "OrderValidationError" in source,
    }

    return checks


def test_stopped():
    print("\n===== TEST 1: PRODUCT STOPPED =====")

    before = db_state()

    execute(
        """
        UPDATE products
        SET product_status = 'STOPPED'
        WHERE product_id = :product_id
        """,
        {"product_id": PRODUCT_ID},
    )

    item = cart_target()
    after = db_state()

    add_result(
        "STOPPED - Cart item preserved",
        item is not None,
        "cart item exists",
        item,
    )

    add_result(
        "STOPPED - product status visible",
        item is not None
        and item["product_status"] == "STOPPED",
        "STOPPED",
        None if item is None else item["product_status"],
    )

    add_result(
        "STOPPED - purchasing disabled",
        item is not None
        and item["purchasable"] is False,
        False,
        None if item is None else item["purchasable"],
    )

    add_result(
        "STOPPED - unavailable reason exists",
        item is not None
        and bool(item["unavailable_reason"]),
        "non-empty reason",
        None if item is None else item["unavailable_reason"],
    )

    add_result(
        "STOPPED - Cart quantity unchanged",
        before["cart"]["quantity"] == after["cart"]["quantity"],
        before["cart"]["quantity"],
        after["cart"]["quantity"],
    )

    add_result(
        "STOPPED - Inventory unchanged",
        before["inventory"]["reserved_quantity"]
        == after["inventory"]["reserved_quantity"],
        before["inventory"]["reserved_quantity"],
        after["inventory"]["reserved_quantity"],
    )


def test_variant_inactive():
    print("\n===== TEST 2: VARIANT INACTIVE =====")

    before = db_state()

    execute(
        """
        UPDATE product_variants
        SET active_yn = 'N'
        WHERE variant_id = :variant_id
        """,
        {"variant_id": VARIANT_ID},
    )

    item = cart_target()
    after = db_state()

    add_result(
        "INACTIVE - Cart item preserved",
        item is not None,
        "cart item exists",
        item,
    )

    add_result(
        "INACTIVE - active_yn visible",
        item is not None
        and item["variant_active_yn"] == "N",
        "N",
        None if item is None else item["variant_active_yn"],
    )

    add_result(
        "INACTIVE - purchasing disabled",
        item is not None
        and item["purchasable"] is False,
        False,
        None if item is None else item["purchasable"],
    )

    add_result(
        "INACTIVE - unavailable reason exists",
        item is not None
        and bool(item["unavailable_reason"]),
        "non-empty reason",
        None if item is None else item["unavailable_reason"],
    )

    add_result(
        "INACTIVE - Cart unchanged",
        before["cart"]["quantity"] == after["cart"]["quantity"],
        before["cart"]["quantity"],
        after["cart"]["quantity"],
    )

    add_result(
        "INACTIVE - Inventory unchanged",
        before["inventory"]["reserved_quantity"]
        == after["inventory"]["reserved_quantity"],
        before["inventory"]["reserved_quantity"],
        after["inventory"]["reserved_quantity"],
    )


def test_inventory_shortage():
    print("\n===== TEST 3: INVENTORY SHORTAGE =====")

    before = db_state()
    inv = before["inventory"]

    # available quantity를 0으로 만드는 임시 상태.
    # stock = reserved + safety 로 맞춘다.
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

    item = cart_target()
    after = db_state()

    add_result(
        "SHORTAGE - available quantity is zero",
        int(after["inventory"]["available_quantity"]) == 0,
        0,
        after["inventory"]["available_quantity"],
    )

    add_result(
        "SHORTAGE - Cart item preserved",
        item is not None,
        "cart item exists",
        item,
    )

    add_result(
        "SHORTAGE - purchasing disabled",
        item is not None
        and item["purchasable"] is False,
        False,
        None if item is None else item["purchasable"],
    )

    add_result(
        "SHORTAGE - unavailable reason exists",
        item is not None
        and bool(item["unavailable_reason"]),
        "non-empty reason",
        None if item is None else item["unavailable_reason"],
    )

    add_result(
        "SHORTAGE - Cart quantity unchanged",
        before["cart"]["quantity"] == after["cart"]["quantity"],
        before["cart"]["quantity"],
        after["cart"]["quantity"],
    )

    add_result(
        "SHORTAGE - reserved quantity unchanged",
        before["inventory"]["reserved_quantity"]
        == after["inventory"]["reserved_quantity"],
        before["inventory"]["reserved_quantity"],
        after["inventory"]["reserved_quantity"],
    )


def restore():
    print("\n===== RESTORE =====")

    if not original:
        return

    execute(
        """
        UPDATE products
        SET sale_price = :sale_price,
            product_status = :product_status
        WHERE product_id = :product_id
        """,
        {
            "sale_price": original["product"]["sale_price"],
            "product_status": original["product"]["product_status"],
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
            "active_yn": original["variant"]["active_yn"],
            "variant_id": VARIANT_ID,
        },
    )

    execute(
        """
        UPDATE inventories
        SET stock_quantity = :stock_quantity,
            reserved_quantity = :reserved_quantity,
            safety_stock = :safety_stock
        WHERE org_id = :org_id
          AND variant_id = :variant_id
        """,
        {
            "stock_quantity":
                original["inventory"]["stock_quantity"],
            "reserved_quantity":
                original["inventory"]["reserved_quantity"],
            "safety_stock":
                original["inventory"]["safety_stock"],
            "org_id": ORG_ID,
            "variant_id": VARIANT_ID,
        },
    )


def final_restore_check():
    print("\n===== FINAL RESTORE CHECK =====")

    final = db_state()

    comparisons = {
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

    for name, passed in comparisons.items():
        add_result(
            f"RESTORE - {name}",
            passed,
            "same as BEFORE",
            "same" if passed else "DIFFERENT",
        )

    return final


def write_reports(before, final, source_checks, fatal_error=None):
    timestamp = datetime.now().isoformat(timespec="seconds")

    passed_count = sum(1 for r in results if r["passed"])
    failed_count = sum(1 for r in results if not r["passed"])

    payload = {
        "generated_at": timestamp,
        "target": {
            "buyer_user_id": BUYER_ID,
            "product_id": PRODUCT_ID,
            "variant_id": VARIANT_ID,
            "cart_item_id": CART_ITEM_ID,
            "org_id": ORG_ID,
        },
        "before": before,
        "final": final,
        "order_service_source_checks": source_checks,
        "results": results,
        "fatal_error": fatal_error,
        "summary": {
            "pass": passed_count,
            "fail": failed_count,
            "overall":
                "PASS"
                if failed_count == 0 and not fatal_error
                else "FAIL",
        },
    }

    json_path = EVIDENCE / "buyer_crossflow_result.json"
    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    rows = []
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        rows.append(
            "<tr>"
            f"<td>{html.escape(status)}</td>"
            f"<td>{html.escape(result['name'])}</td>"
            f"<td>{html.escape(result['expected'])}</td>"
            f"<td>{html.escape(result['actual'])}</td>"
            "</tr>"
        )

    source_rows = []
    for name, passed in source_checks.items():
        source_rows.append(
            "<tr>"
            f"<td>{'PASS' if passed else 'FAIL'}</td>"
            f"<td>{html.escape(name)}</td>"
            "</tr>"
        )

    overall = payload["summary"]["overall"]

    document = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>SHOPDB2 구매자 교차경로 자동검증</title>
<style>
body {{
    font-family: Arial, "Malgun Gothic", sans-serif;
    margin: 36px;
    line-height: 1.5;
}}
h1, h2 {{ margin-bottom: 8px; }}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0 28px;
}}
th, td {{
    border: 1px solid #999;
    padding: 8px;
    text-align: left;
    vertical-align: top;
}}
.summary {{
    font-size: 20px;
    font-weight: bold;
    padding: 12px;
    border: 2px solid #333;
}}
pre {{
    white-space: pre-wrap;
    border: 1px solid #bbb;
    padding: 12px;
}}
</style>
</head>
<body>

<h1>SHOPDB2 구매자 교차경로 자동검증</h1>

<p>생성시각: {html.escape(timestamp)}</p>
<p>
대상:
buyer={BUYER_ID},
product={PRODUCT_ID},
variant={VARIANT_ID},
cart_item={CART_ITEM_ID},
org={ORG_ID}
</p>

<div class="summary">
OVERALL: {overall}
<br>
PASS: {passed_count} / FAIL: {failed_count}
</div>

<h2>1. 자동 검증 결과</h2>
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
{''.join(rows)}
</tbody>
</table>

<h2>2. Order Service 차단 로직 소스 확인</h2>
<table>
<thead>
<tr><th>결과</th><th>검사항목</th></tr>
</thead>
<tbody>
{''.join(source_rows)}
</tbody>
</table>

<h2>3. 테스트 전 DB 상태</h2>
<pre>{html.escape(json.dumps(before, ensure_ascii=False, indent=2, default=str))}</pre>

<h2>4. 최종 원복 DB 상태</h2>
<pre>{html.escape(json.dumps(final, ensure_ascii=False, indent=2, default=str))}</pre>

<h2>5. 보안</h2>
<p>
Access Token, Authorization Bearer 값, DB 비밀번호는
이 보고서에 기록하지 않습니다.
</p>

<h2>6. 주의</h2>
<p>
이 보고서의 STOPPED/옵션 비활성/재고 부족 항목은
Cart의 실제 Service 응답과 DB Before/After를 자동 검증합니다.
Order 차단 조건은 현재 order_service.py의 실제 검증 코드 존재 여부를 함께 검사합니다.
실제 HTTP 주문 차단 응답 증빙은 별도 API 테스트 항목입니다.
</p>

</body>
</html>
"""

    html_path = EVIDENCE / "buyer_crossflow_report.html"
    html_path.write_text(document, encoding="utf-8")

    print("\n===== REPORT =====")
    print("JSON :", json_path)
    print("HTML :", html_path)
    print("OVERALL =", overall)


def main():
    global original

    print("SHOPDB2 BUYER CROSS-FLOW AUTOMATED TEST")
    print("======================================")

    original = db_state()

    print("\n===== BEFORE =====")
    print(
        json.dumps(
            original,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    # 안전 사전조건
    if original["product"] is None:
        raise RuntimeError("product_id=1 상품이 없습니다.")

    if original["variant"] is None:
        raise RuntimeError("variant_id=1 옵션이 없습니다.")

    if original["inventory"] is None:
        raise RuntimeError("org=1, variant=1 재고가 없습니다.")

    if original["cart"] is None:
        raise RuntimeError("cart_item_id=52가 없습니다.")

    if original["product"]["product_status"] != "SALE":
        raise RuntimeError(
            "테스트 시작 전 product_status가 SALE이 아닙니다."
        )

    if original["variant"]["active_yn"] != "Y":
        raise RuntimeError(
            "테스트 시작 전 active_yn이 Y가 아닙니다."
        )

    source_checks = inspect_order_service_source()

    for name, passed in source_checks.items():
        add_result(
            f"ORDER SERVICE - {name}",
            passed,
            True,
            passed,
        )

    fatal_error = None
    final = None

    try:
        test_stopped()

        # 다음 테스트 전 상품상태 원복
        execute(
            """
            UPDATE products
            SET product_status = :status
            WHERE product_id = :product_id
            """,
            {
                "status":
                    original["product"]["product_status"],
                "product_id": PRODUCT_ID,
            },
        )

        test_variant_inactive()

        # 다음 테스트 전 옵션상태 원복
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

        test_inventory_shortage()

    except Exception:
        fatal_error = traceback.format_exc()
        print("\n[FATAL]")
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
            print(restore_error)

        write_reports(
            original,
            final,
            source_checks,
            fatal_error,
        )


if __name__ == "__main__":
    main()
