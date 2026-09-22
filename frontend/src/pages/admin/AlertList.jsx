import { useEffect, useState } from "react";
import { fetchAlerts, resolveAlert } from "../../api/admin";

const ALERT_TYPES = ["LOW_STOCK", "WEBHOOK_FAILED", "REFUND_DELAYED"];
const SEVERITY_LABEL = {
  INFO: "정보",
  WARNING: "주의",
  CRITICAL: "긴급",
};
const SEVERITY_COLOR = {
  INFO: "#6b7280",
  WARNING: "#d97706",
  CRITICAL: "#dc2626",
};

const PAGE_SIZE = 20;

function AlertList() {
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [resolvedYn, setResolvedYn] = useState("N");
  const [alertType, setAlertType] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  function loadAlerts() {
    setLoading(true);
    fetchAlerts({
      resolved_yn: resolvedYn,
      alert_type: alertType,
      skip: page * PAGE_SIZE,
      limit: PAGE_SIZE,
    })
      .then((data) => {
        setAlerts(data.items);
        setTotal(data.total);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadAlerts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resolvedYn, alertType, page]);

  function handleFilterChange(setter) {
    return (event) => {
      setPage(0);
      setter(event.target.value);
    };
  }

  async function handleResolve(alert) {
    if (!confirm(`${alert.alert_code} 알림을 해결 처리하시겠습니까?`)) return;
    try {
      await resolveAlert(alert.alert_id);
      loadAlerts();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="admin-page-header">
        <h1>시스템 알림</h1>
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={resolvedYn} onChange={handleFilterChange(setResolvedYn)}>
          <option value="N">미해결</option>
          <option value="Y">해결됨</option>
          <option value="">전체</option>
        </select>

        <select value={alertType} onChange={handleFilterChange(setAlertType)}>
          <option value="">전체 유형</option>
          {ALERT_TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      {loading ? (
        <p>불러오는 중...</p>
      ) : (
        <>
          <table className="admin-table">
            <thead>
              <tr>
                <th>발생일시</th>
                <th>유형</th>
                <th>심각도</th>
                <th>대상</th>
                <th>상태</th>
                <th>동작</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a.alert_id}>
                  <td>{new Date(a.created_at).toLocaleString()}</td>
                  <td>{a.alert_type}</td>
                  <td>
                    <span style={{ color: SEVERITY_COLOR[a.severity], fontWeight: "bold" }}>
                      {SEVERITY_LABEL[a.severity] ?? a.severity}
                    </span>
                  </td>
                  <td>{a.target_table} #{a.target_id ?? "-"}</td>
                  <td>{a.resolved_yn === "Y" ? "해결됨" : "미해결"}</td>
                  <td>
                    {a.resolved_yn === "N" && (
                      <button onClick={() => handleResolve(a)}>해결 처리</button>
                    )}
                  </td>
                </tr>
              ))}
              {alerts.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", color: "#9ca3af" }}>
                    표시할 알림이 없습니다.
                  </td>
                </tr>
              )}
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

export default AlertList;