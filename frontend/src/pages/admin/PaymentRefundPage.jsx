import { useEffect, useState } from "react";
import {
  fetchAdminPayments,
  fetchAdminRefunds,
  forceCancelPayment,
  approveRefund,
  rejectRefund,
} from "../../api/admin";

const PAGE_SIZE = 20;

function PaymentRefundPage() {
  const [tab, setTab] = useState("payments"); // payments | refunds
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  function loadData() {
    setLoading(true);
    const loader =
      tab === "payments"
        ? fetchAdminPayments({
            payment_status: statusFilter,
            skip: page * PAGE_SIZE,
            limit: PAGE_SIZE,
          })
        : fetchAdminRefunds({
            refund_status: statusFilter,
            skip: page * PAGE_SIZE,
            limit: PAGE_SIZE,
          });

    loader
      .then((data) => {
        setRows(data.items);
        setTotal(data.total);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, statusFilter, page]);

  function handleTabChange(nextTab) {
    setTab(nextTab);
    setStatusFilter("");
    setPage(0);
  }

  async function handleForceCancel(payment) {
    if (!confirm(`주문 ${payment.order_no} 결제를 강제 취소하시겠습니까?`)) return;
    try {
      await forceCancelPayment(payment.payment_id);
      loadData();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  async function handleApprove(refund) {
    if (!confirm(`주문 ${refund.order_no} 환불을 승인하시겠습니까? (${refund.requested_amount}원)`)) return;
    try {
      await approveRefund(refund.refund_request_id);
      loadData();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  async function handleReject(refund) {
    if (!confirm(`주문 ${refund.order_no} 환불을 거절하시겠습니까?`)) return;
    try {
      await rejectRefund(refund.refund_request_id);
      loadData();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="admin-page-header">
        <h1>결제/환불관리</h1>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button
          onClick={() => handleTabChange("payments")}
          style={{ fontWeight: tab === "payments" ? "bold" : "normal" }}
        >
          결제 관리
        </button>
        <button
          onClick={() => handleTabChange("refunds")}
          style={{ fontWeight: tab === "refunds" ? "bold" : "normal" }}
        >
          환불 관리
        </button>
      </div>

      <div style={{ marginBottom: 16 }}>
        <select
          value={statusFilter}
          onChange={(e) => {
            setPage(0);
            setStatusFilter(e.target.value);
          }}
        >
          <option value="">전체 상태</option>
          {tab === "payments"
            ? ["DONE", "CANCELED", "PARTIAL_CANCELED"].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))
            : ["REQUESTED", "REVIEWING", "APPROVED", "REJECTED", "COMPLETED"].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
        </select>
      </div>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      {loading ? (
        <p>불러오는 중...</p>
      ) : tab === "payments" ? (
        <table className="admin-table">
          <thead>
            <tr>
              <th>주문번호</th>
              <th>구매자</th>
              <th>PG사</th>
              <th>상태</th>
              <th>요청금액</th>
              <th>승인금액</th>
              <th>잔액</th>
              <th>동작</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.payment_id}>
                <td>{p.order_no}</td>
                <td>{p.buyer_name}</td>
                <td>{p.pg_provider}</td>
                <td>{p.payment_status}</td>
                <td>{p.requested_amount}</td>
                <td>{p.approved_amount}</td>
                <td>{p.balance_amount}</td>
                <td>
                  {p.payment_status !== "CANCELED" && Number(p.balance_amount) > 0 && (
                    <button onClick={() => handleForceCancel(p)}>강제취소</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>주문번호</th>
              <th>구매자</th>
              <th>사유</th>
              <th>요청금액</th>
              <th>승인금액</th>
              <th>상태</th>
              <th>동작</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.refund_request_id}>
                <td>{r.order_no}</td>
                <td>{r.buyer_name}</td>
                <td>{r.refund_reason}</td>
                <td>{r.requested_amount}</td>
                <td>{r.approved_amount ?? "-"}</td>
                <td>{r.refund_status}</td>
                <td>
                  {["REQUESTED", "REVIEWING"].includes(r.refund_status) && (
                    <>
                      <button onClick={() => handleApprove(r)}>승인</button>
                      <button onClick={() => handleReject(r)}>거절</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
        <button disabled={page === 0} onClick={() => setPage((p) => p - 1)}>이전</button>
        <span>{page + 1} / {totalPages} (총 {total}건)</span>
        <button disabled={page + 1 >= totalPages} onClick={() => setPage((p) => p + 1)}>다음</button>
      </div>
    </div>
  );
}

export default PaymentRefundPage;