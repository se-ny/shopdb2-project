import { useEffect, useState } from "react";
import { fetchDashboardSummary } from "../../api/admin";

const SEVERITY_COLOR = { INFO: "#6b7280", WARNING: "#d97706", CRITICAL: "#dc2626" };

function StatCard({ label, value, highlight }) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: 8,
        padding: 16,
        flex: 1,
        minWidth: 160,
        background: highlight ? "#fef2f2" : "#fff",
      }}
    >
      <p style={{ margin: 0, fontSize: 13, color: "#6b7280" }}>{label}</p>
      <p style={{ margin: "8px 0 0", fontSize: 24, fontWeight: "bold" }}>{value}</p>
    </div>
  );
}

function Dashboard() {
  const [data, setData] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardSummary()
      .then(setData)
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <div className="admin-page-header">
        <h1>대시보드</h1>
      </div>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 24 }}>
        <StatCard label="오늘 주문 수" value={`${data.today_order_count}건`} />
        <StatCard label="오늘 결제 매출" value={`${data.today_revenue.toLocaleString()}원`} />
        <StatCard label="대기 중인 환불" value={`${data.pending_refund_count}건`} />
        <StatCard
          label="미해결 알림"
          value={`${data.unresolved_alert_count}건 (긴급 ${data.unresolved_critical_alert_count})`}
          highlight={data.unresolved_critical_alert_count > 0}
        />
      </div>

      <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
        <div style={{ flex: 1, minWidth: 320 }}>
          <h2 className="policy-section-title">최근 주문</h2>
          <table className="admin-table">
            <thead>
              <tr>
                <th>주문번호</th>
                <th>구매자</th>
                <th>상태</th>
                <th>금액</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_orders.map((o) => (
                <tr key={o.order_id}>
                  <td>{o.order_no}</td>
                  <td>{o.buyer_name}</td>
                  <td>{o.order_status}</td>
                  <td>{o.total_amount}</td>
                </tr>
              ))}
              {data.recent_orders.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: "center", color: "#9ca3af" }}>주문이 없습니다.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <div style={{ flex: 1, minWidth: 320 }}>
          <h2 className="policy-section-title">미해결 알림</h2>
          <table className="admin-table">
            <thead>
              <tr>
                <th>유형</th>
                <th>심각도</th>
                <th>대상</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_alerts.map((a) => (
                <tr key={a.alert_id}>
                  <td>{a.alert_type}</td>
                  <td style={{ color: SEVERITY_COLOR[a.severity], fontWeight: "bold" }}>{a.severity}</td>
                  <td>{a.target_table} #{a.target_id ?? "-"}</td>
                </tr>
              ))}
              {data.recent_alerts.length === 0 && (
                <tr><td colSpan={3} style={{ textAlign: "center", color: "#9ca3af" }}>미해결 알림이 없습니다.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;