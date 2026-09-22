import { useEffect, useState } from "react";
import {
  deleteCartItem,
  getCart,
  updateCartItem,
} from "../../api/buyer";
import "../../styles/buyer.css";

function money(value) {
  return `${Number(value || 0).toLocaleString("ko-KR")}원`;
}

export default function BuyerCart({ onCheckout }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [workingId, setWorkingId] = useState(null);
  const [error, setError] = useState("");

  async function loadCart() {
    try {
      setLoading(true);
      setError("");
      setCart(await getCart());
    } catch (err) {
      setError(err.message || "장바구니를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCart();
  }, []);

  async function changeQuantity(item, quantity) {
    if (quantity < 1) return;

    try {
      setWorkingId(item.cart_item_id);
      setError("");
      setCart(await updateCartItem(item.cart_item_id, quantity));
    } catch (err) {
      setError(err.message || "수량 변경에 실패했습니다.");
    } finally {
      setWorkingId(null);
    }
  }

  async function removeItem(item) {
    if (!window.confirm(`${item.product_name}을(를) 장바구니에서 삭제할까요?`)) {
      return;
    }

    try {
      setWorkingId(item.cart_item_id);
      setError("");
      setCart(await deleteCartItem(item.cart_item_id));
    } catch (err) {
      setError(err.message || "상품 삭제에 실패했습니다.");
    } finally {
      setWorkingId(null);
    }
  }

  if (loading) {
    return <div className="buyer-state">장바구니를 불러오는 중입니다.</div>;
  }

  const items = cart?.items || [];
  const purchasableItems = items.filter((item) => item.purchasable);

  return (
    <section className="buyer-page">
      <div className="buyer-page-header">
        <div>
          <p className="buyer-eyebrow">SHOPDB2 BUYER</p>
          <h1>장바구니</h1>
          <p>상품 상태와 현재 가격을 다시 확인하고 주문할 수 있습니다.</p>
        </div>
        <span className="buyer-count">{cart?.total_quantity || 0}개</span>
      </div>

      {error && <div className="buyer-alert buyer-alert--error">{error}</div>}

      {items.length === 0 ? (
        <div className="buyer-empty">
          <strong>장바구니가 비어 있습니다.</strong>
          <p>상품을 선택해 장바구니에 담아보세요.</p>
        </div>
      ) : (
        <>
          <div className="buyer-cart-list">
            {items.map((item) => (
              <article
                className={`buyer-cart-item ${!item.purchasable ? "buyer-cart-item--disabled" : ""}`}
                key={item.cart_item_id}
              >
                <div className="buyer-cart-main">
                  <div>
                    <div className="buyer-row">
                      <h3>{item.product_name}</h3>
                      <span className={item.purchasable ? "buyer-badge" : "buyer-badge buyer-badge--danger"}>
                        {item.purchasable ? "구매 가능" : "구매 불가"}
                      </span>
                    </div>

                    <p className="buyer-muted">
                      {item.option_name1 && `${item.option_name1}: ${item.option_value1}`}
                      {item.option_name2 && ` · ${item.option_name2}: ${item.option_value2}`}
                    </p>

                    {item.price_changed && (
                      <div className="buyer-alert buyer-alert--warning">
                        장바구니에 담은 뒤 가격이 변경되었습니다.
                        현재 가격 {money(item.current_unit_price)}을 기준으로 주문됩니다.
                      </div>
                    )}

                    {!item.purchasable && (
                      <div className="buyer-alert buyer-alert--error">
                        {item.unavailable_reason || "현재 구매할 수 없는 상품입니다."}
                      </div>
                    )}
                  </div>

                  <strong className="buyer-price">
                    {money(item.current_unit_price)}
                  </strong>
                </div>

                <div className="buyer-cart-actions">
                  <div className="buyer-quantity">
                    <button
                      type="button"
                      disabled={workingId === item.cart_item_id || item.quantity <= 1}
                      onClick={() => changeQuantity(item, item.quantity - 1)}
                    >
                      −
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      type="button"
                      disabled={
                        workingId === item.cart_item_id ||
                        !item.purchasable ||
                        item.quantity >= item.available_quantity
                      }
                      onClick={() => changeQuantity(item, item.quantity + 1)}
                    >
                      +
                    </button>
                  </div>

                  <span className="buyer-muted">
                    구매 가능 {item.available_quantity}개
                  </span>

                  <strong>{money(item.current_unit_price * item.quantity)}</strong>

                  <button
                    type="button"
                    className="buyer-link-button"
                    disabled={workingId === item.cart_item_id}
                    onClick={() => removeItem(item)}
                  >
                    삭제
                  </button>
                </div>
              </article>
            ))}
          </div>

          <aside className="buyer-summary">
            <div>
              <span>상품 종류</span>
              <strong>{cart.total_item_count}개</strong>
            </div>
            <div>
              <span>총 수량</span>
              <strong>{cart.total_quantity}개</strong>
            </div>
            <div className="buyer-summary-total">
              <span>현재 상품금액</span>
              <strong>{money(cart.current_total_amount)}</strong>
            </div>

            {purchasableItems.length !== items.length && (
              <p className="buyer-summary-notice">
                구매할 수 없는 상품이 포함되어 있습니다. 상태를 확인하거나 삭제한 뒤 주문해 주세요.
              </p>
            )}

            <button
              type="button"
              className="buyer-primary-button"
              disabled={
                items.length === 0 ||
                purchasableItems.length !== items.length
              }
              onClick={() => onCheckout?.(items)}
            >
              주문하기
            </button>
          </aside>
        </>
      )}
    </section>
  );
}
