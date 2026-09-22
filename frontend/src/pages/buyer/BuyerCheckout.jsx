import { useState } from "react";
import { createOrder } from "../../api/buyer";
import "../../styles/buyer.css";

function money(value) {
  return `${Number(value || 0).toLocaleString("ko-KR")}원`;
}

export default function BuyerCheckout({ items = [], onCreated, onBack }) {
  const [form, setForm] = useState({
    receiver_name: "",
    receiver_phone: "",
    zipcode: "",
    shipping_address1: "",
    shipping_address2: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const total = items.reduce(
    (sum, item) => sum + Number(item.current_unit_price) * Number(item.quantity),
    0,
  );

  function change(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();

    if (!items.length) {
      setError("주문할 상품이 없습니다.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const order = await createOrder({
        items: items.map((item) => ({
          product_id: item.product_id,
          variant_id: item.variant_id,
          quantity: item.quantity,
          cart_item_id: item.cart_item_id,
        })),
        receiver_name: form.receiver_name.trim(),
        receiver_phone: form.receiver_phone.trim(),
        zipcode: form.zipcode.trim() || null,
        shipping_address1: form.shipping_address1.trim(),
        shipping_address2: form.shipping_address2.trim() || null,
      });

      onCreated?.(order);
    } catch (err) {
      setError(err.message || "주문 생성에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="buyer-page buyer-checkout">
      <button type="button" className="buyer-back-button" onClick={onBack}>
        ← 장바구니로
      </button>

      <div className="buyer-page-header">
        <div>
          <p className="buyer-eyebrow">ORDER CHECK</p>
          <h1>주문 확인</h1>
          <p>결제 전에 상품, 수량, 배송정보와 금액을 다시 확인하세요.</p>
        </div>
      </div>

      {error && <div className="buyer-alert buyer-alert--error">{error}</div>}

      <div className="buyer-checkout-grid">
        <div>
          <h2>주문 상품</h2>
          <div className="buyer-panel">
            {items.map((item) => (
              <div className="buyer-order-line" key={item.cart_item_id}>
                <div>
                  <strong>{item.product_name}</strong>
                  <p className="buyer-muted">수량 {item.quantity}개</p>
                </div>
                <strong>{money(item.current_unit_price * item.quantity)}</strong>
              </div>
            ))}
          </div>

          <h2>배송 정보</h2>
          <form id="buyer-order-form" className="buyer-panel buyer-form" onSubmit={submit}>
            <label>
              받는 분 *
              <input
                name="receiver_name"
                value={form.receiver_name}
                onChange={change}
                required
              />
            </label>

            <label>
              연락처 *
              <input
                name="receiver_phone"
                value={form.receiver_phone}
                onChange={change}
                placeholder="010-0000-0000"
                required
              />
            </label>

            <label>
              우편번호
              <input name="zipcode" value={form.zipcode} onChange={change} />
            </label>

            <label>
              주소 *
              <input
                name="shipping_address1"
                value={form.shipping_address1}
                onChange={change}
                required
              />
            </label>

            <label>
              상세주소
              <input
                name="shipping_address2"
                value={form.shipping_address2}
                onChange={change}
              />
            </label>
          </form>
        </div>

        <aside className="buyer-summary buyer-summary--sticky">
          <div>
            <span>상품금액</span>
            <strong>{money(total)}</strong>
          </div>
          <div>
            <span>배송비</span>
            <strong>0원</strong>
          </div>
          <div className="buyer-summary-total">
            <span>결제 예정금액</span>
            <strong>{money(total)}</strong>
          </div>

          <p className="buyer-summary-notice">
            주문 버튼을 누르면 현재 재고를 다시 검증하고 주문 재고가 예약됩니다.
          </p>

          <button
            form="buyer-order-form"
            type="submit"
            className="buyer-primary-button"
            disabled={submitting}
          >
            {submitting ? "주문 처리 중..." : `${money(total)} 주문 확정`}
          </button>
        </aside>
      </div>
    </section>
  );
}
