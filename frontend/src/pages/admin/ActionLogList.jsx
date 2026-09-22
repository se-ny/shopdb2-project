import { useEffect, useState } from "react";
import { fetchActionLogs } from "../../api/admin";

const ACTION_TYPES = [
  "ROLE_ASSIGN", "ROLE_REVOKE",
  "POLICY_CREATE", "POLICY_EXPIRE",
  "ORG_UPDATE", "ORG_DEACTIVATE",
  "PAYMENT_FORCE_CANCEL",
  "REFUND_APPROVE", "REFUND_REJECT",
];

const PAGE_SIZE = 20;

function ActionLogList() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [actionType, setActionType] = useState("");
  const [targetTable, setTargetTable] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [expandedLogId, setExpandedLogId] = useState(null);

  function loadLogs() {
    setLoading(true);
    fetchActionLogs({
      action_type: actionType,
      target_table: targetTable,
      skip: page * PAGE_SIZE,
      limit: PAGE_SIZE,
    })
      .then((data) => {
        setLogs(data.items);
        setTotal(data.total);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, actionType, targetTable]);

  function handleFilterChange(setter) {
    return (event) => {
      setPage(0);
      setter(event.target.value);
    };
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <div className="admin-page-header">
        <h1>관리자 활동 로그</h1>
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={actionType} onChange={handleFilterChange(setActionType)}>
          <option value="">전체 액션</option>
          {ACTION_TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>

        <input
          placeholder="대상 테이블 (예: org_units)"
          value={targetTable}
          onChange={handleFilterChange(setTargetTable)}
        />
      </div>

      {loading ? (
        <p>불러오는 중...</p>
      ) : (
        <>
          <table className="admin-table">
            <thead>
              <tr>
                <th>일시</th>
                <th>처리자</th>
                <th>액션</th>
                <th>대상</th>
                <th>상세</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <>
                  <tr key={log.log_id}>
                    <td>{new Date(log.created_at).toLocaleString()}</td>
                    <td>{log.admin_user_name}</td>
                    <td>{log.action_type}</td>
                    <td>{log.target_table} #{log.target_id ?? "-"}</td>
                    <td>
                      <button
                        onClick={() =>
                          setExpandedLogId(expandedLogId === log.log_id ? null : log.log_id)
                        }
                      >
                        {expandedLogId === log.log_id ? "닫기" : "보기"}
                      </button>
                    </td>
                  </tr>
                  {expandedLogId === log.log_id && (
                    <tr key={`${log.log_id}-detail`}>
                      <td colSpan={5}>
                        <div style={{ display: "flex", gap: 16 }}>
                          <div style={{ flex: 1 }}>
                            <strong>변경 전</strong>
                            <pre style={{ background: "#f5f5f5", padding: 8, overflowX: "auto" }}>
                              {log.before_value ? JSON.stringify(log.before_value, null, 2) : "-"}
                            </pre>
                          </div>
                          <div style={{ flex: 1 }}>
                            <strong>변경 후</strong>
                            <pre style={{ background: "#f5f5f5", padding: 8, overflowX: "auto" }}>
                              {log.after_value ? JSON.stringify(log.after_value, null, 2) : "-"}
                            </pre>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>

          <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
            <button disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
              이전
            </button>
            <span>{page + 1} / {totalPages} (총 {total}건)</span>
            <button disabled={page + 1 >= totalPages} onClick={() => setPage((p) => p + 1)}>
              다음
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default ActionLogList;