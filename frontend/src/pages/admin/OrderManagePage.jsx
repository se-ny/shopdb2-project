import { useEffect, useState } from "react";
import { fetchAdminOrders, fetchAdminOrderDetail } from "../../api/admin";

const ORDER_STATUSES = [
  "ORDERED", "PAYMENT_PENDING", "PAID", "PREPARING",
  "SHIPPING", "DELIVERED", "COMPLETED", "CANCELLED", "REFUNDED",
];

const PAGE_SIZE = 20;

function OrderManagePage() {
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  function loadOrders() {
    setLoading(true);
    fetchAdminOrders({
      order_status: statusFilter,
      skip: page * PAGE_SIZE,
      limit: PAGE_SIZE,
    })
      .then((data) => {
        setOrders(data.items);
        setTotal(data.total);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, page]);

  async function handleViewDetail(orderId) {
    setDetailLoading(true);
    try {
      const data = await fetchAdminOrderDetail(orderId);
      setDetail(data);
    } catch (error) {
      alert(`조회 실패: ${error.message}`);
    } finally {
      setDetailLoading(false);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="admin-page-header">
        <h1>주문관리</h1>
      </div>

      <div style={{ marginBottom: 16 }}>
        <select
          value={statusFilter}
          onChange={(e) => { setPage(0); setStatusFilter(e.target.value); }}
        >
          <option value="">전체 상태</option>
          {ORDER_STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      {detail && (
        <div className="rag-answer-box" style={{ marginBottom: 16 }}>
          <div className="admin-page-header">
            <h2 className="policy-section-title" style={{ margin: 0 }}>
              주문 상세 · {detail.order_no}
            </h2>
            <button onClick={() => setDetail(null)}>닫기</button>
          </div>
          <p style={{ fontSize: 14 }}>
            구매자: {detail.buyer_name} · 상태: {detail.order_status} · 총액: {detail.total_amount}
          </p>
          <p style={{ fontSize: 14 }}>
            배송지: [{detail.zipcode}] {detail.shipping_address1} {detail.shipping_address2}
            ({detail.receiver_name} / {detail.receiver_phone})
          </p>
          <table className="admin-table">
            <thead>
              <tr>
                <th>상품명</th>
                <th>옵션</th>
                <th>수량</th>
                <th>단가</th>
                <th>금액</th>
                <th>상태</th>
              </tr>
            </thead>
            <tbody>
              {detail.items.map((item) => (
                <tr key={item.order_item_id}>
                  <td>{item.product_name_snapshot}</td>
                  <td>{item.sku_snapshot ?? "-"}</td>
                  <td>{item.quantity}</td>
                  <td>{item.unit_price}</td>
                  <td>{item.item_amount}</td>
                  <td>{item.item_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {loading ? (
        <p>불러오는 중...</p>
      ) : (
        <>
          <table className="admin-table">
            <thead>
              <tr>
                <th>주문번호</th>
                <th>구매자</th>
                <th>조직</th>
                <th>상태</th>
                <th>총액</th>
                <th>주문일시</th>
                <th>동작</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.order_id}>
                  <td>{o.order_no}</td>
                  <td>{o.buyer_name}</td>
                  <td>{o.org_name}</td>
                  <td>{o.order_status}</td>
                  <td>{o.total_amount}</td>
                  <td>{new Date(o.ordered_at).toLocaleString()}</td>
                  <td>
                    <button
                      onClick={() => handleViewDetail(o.order_id)}
                      disabled={detailLoading}
                    >
                      상세보기
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
            <button disabled={page === 0} onClick={() => setPage((p) => p - 1)}>이전</button>
            <span>{page + 1} / {totalPages} (총 {total}건)</span>
            <button disabled={page + 1 >= totalPages} onClick={() => setPage((p) => p + 1)}>다음</button>
          </div>
        </>
      )}
    </div>
  );
}

export default OrderManagePage;