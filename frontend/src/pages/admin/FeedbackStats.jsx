import { useEffect, useState } from "react";
import { fetchFeedbackList, fetchFeedbackStats } from "../../api/admin";

const PAGE_SIZE = 20;

function FeedbackStats() {
  const [stats, setStats] = useState(null);
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [sourceType, setSourceType] = useState("");
  const [score, setScore] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  function loadAll() {
    setLoading(true);
    Promise.all([
      fetchFeedbackStats(),
      fetchFeedbackList({
        source_type: sourceType,
        feedback_score: score,
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
      }),
    ])
      .then(([statsData, listData]) => {
        setStats(statsData);
        setItems(listData.items);
        setTotal(listData.total);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sourceType, score, page]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <div className="admin-page-header">
        <h1>AI 응답 피드백</h1>
      </div>

      {stats && (
        <div style={{ display: "flex", gap: 24, marginBottom: 20 }}>
          {Object.entries(stats).map(([source, counts]) => {
            const sum = counts.GOOD + counts.BAD;
            const rate = sum > 0 ? Math.round((counts.GOOD / sum) * 100) : 0;
            return (
              <div key={source} style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: 16, minWidth: 160 }}>
                <strong>{source}</strong>
                <p style={{ margin: "8px 0 0", fontSize: 13 }}>👍 {counts.GOOD} · 👎 {counts.BAD}</p>
                <p style={{ margin: 0, fontSize: 13, color: "#6b7280" }}>긍정 비율 {rate}%</p>
              </div>
            );
          })}
        </div>
      )}

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={sourceType} onChange={(e) => { setPage(0); setSourceType(e.target.value); }}>
          <option value="">전체 소스</option>
          <option value="RAG">RAG</option>
          <option value="SQL_AGENT">SQL_AGENT</option>
        </select>
        <select value={score} onChange={(e) => { setPage(0); setScore(e.target.value); }}>
          <option value="">전체</option>
          <option value="GOOD">GOOD</option>
          <option value="BAD">BAD</option>
        </select>
      </div>

      {loading ? (
        <p>불러오는 중...</p>
      ) : (
        <>
          <table className="admin-table">
            <thead>
              <tr>
                <th>일시</th>
                <th>소스</th>
                <th>로그ID</th>
                <th>평가</th>
                <th>사유</th>
              </tr>
            </thead>
            <tbody>
              {items.map((f) => (
                <tr key={f.feedback_id}>
                  <td>{new Date(f.created_at).toLocaleString()}</td>
                  <td>{f.source_type}</td>
                  <td>{f.source_log_id}</td>
                  <td>{f.feedback_score === "GOOD" ? "👍" : "👎"}</td>
                  <td>{f.feedback_reason ?? "-"}</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", color: "#9ca3af" }}>
                    피드백이 없습니다.
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

export default FeedbackStats;