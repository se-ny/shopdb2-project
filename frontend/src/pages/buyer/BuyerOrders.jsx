import { useEffect, useState } from "react";
import { getOrders } from "../../api/buyer";
import "../../styles/buyer.css";

function money(value) {
  return `${Number(value || 0).toLocaleString("ko-KR")}원`;
}

const STATUS = {
  ORDERED: "주문 완료",
  PAYMENT_PENDING: "결제 대기",
  PAID: "결제 완료",
  CANCELLED: "주문 취소",
};

export default function BuyerOrders({ onSelect }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setOrders(await getOrders());
      } catch (err) {
        setError(err.message || "주문내역을 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <section className="buyer-page">
      <div className="buyer-page-header">
        <div>
          <p className="buyer-eyebrow">MY ORDERS</p>
          <h1>주문내역</h1>
          <p>주문 상태와 결제금액을 확인할 수 있습니다.</p>
        </div>
      </div>

      {loading && <div className="buyer-state">주문내역을 불러오는 중입니다.</div>}
      {error && <div className="buyer-alert buyer-alert--error">{error}</div>}

      {!loading && !error && orders.length === 0 && (
        <div className="buyer-empty">
          <strong>아직 주문내역이 없습니다.</strong>
        </div>
      )}

      <div className="buyer-order-list">
        {orders.map((order) => (
          <button
            type="button"
            className="buyer-order-card"
            key={order.order_id}
            onClick={() => onSelect?.(order)}
          >
            <div>
              <span className="buyer-badge">
                {STATUS[order.order_status] || order.order_status}
              </span>
              <h3>{order.order_no}</h3>
              <p className="buyer-muted">
                {order.ordered_at ? new Date(order.ordered_at).toLocaleString("ko-KR") : ""}
              </p>
            </div>
            <strong className="buyer-price">{money(order.total_amount)}</strong>
          </button>
        ))}
      </div>
    </section>
  );
}
