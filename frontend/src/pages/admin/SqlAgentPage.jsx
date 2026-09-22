import { useEffect, useState } from "react";
import { querySqlAgent, fetchSqlAgentLogs } from "../../api/admin";

const PAGE_SIZE = 10;

const STATUS_LABEL = {
  SUCCESS: "성공",
  BLOCKED: "차단됨",
  ERROR: "오류",
};

const STATUS_COLOR = {
  SUCCESS: "#16a34a",
  BLOCKED: "#dc2626",
  ERROR: "#d97706",
};

function SqlAgentPage() {
  const [question, setQuestion] = useState("");
  const [providerCode, setProviderCode] = useState("OLLAMA");
  const [result, setResult] = useState(null);
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryError, setQueryError] = useState("");

  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [logsLoading, setLogsLoading] = useState(true);

  function loadLogs() {
    setLogsLoading(true);
    fetchSqlAgentLogs({ skip: page * PAGE_SIZE, limit: PAGE_SIZE })
      .then((data) => {
        setLogs(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLogsLoading(false));
  }

  useEffect(() => {
    loadLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  async function handleSubmit(event) {
    event.preventDefault();
    setQueryLoading(true);
    setQueryError("");
    setResult(null);
    try {
      const data = await querySqlAgent({ question, provider_code: providerCode });
      setResult(data);
      loadLogs();
    } catch (error) {
      setQueryError(error.message);
    } finally {
      setQueryLoading(false);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="admin-page-header">
        <h1>자연어 SQL 에이전트</h1>
      </div>

      <form onSubmit={handleSubmit} className="rag-query-form">
        <select value={providerCode} onChange={(e) => setProviderCode(e.target.value)}>
          <option value="OLLAMA">OLLAMA</option>
          <option value="OPENAI">OPENAI</option>
          <option value="GEMINI">GEMINI</option>
        </select>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="질문을 입력하세요 (예: 가장 최근 주문 5건 보여줘)"
        />
        <button type="submit" disabled={queryLoading || !question}>
          {queryLoading ? "조회 중..." : "질문하기"}
        </button>
      </form>

      {queryError && <p className="error-message">{queryError}</p>}

      {result && (
        <div className="rag-answer-box">
          <p style={{ margin: 0 }}>
            <strong style={{ color: STATUS_COLOR[result.execution_status] }}>
              {STATUS_LABEL[result.execution_status] ?? result.execution_status}
            </strong>
            {" · "}
            <span style={{ fontSize: 13, color: "#6b7280" }}>{result.response_time_ms}ms</span>
          </p>

          <pre style={{ background: "#f5f5f5", padding: 8, overflowX: "auto", marginTop: 8 }}>
            {result.generated_sql}
          </pre>

          <p className="rag-answer-text">{result.result_summary}</p>

          {result.rows.length > 0 && (
            <div style={{ overflowX: "auto" }}>
              <table className="admin-table">
                <thead>
                  <tr>
                    {result.columns.map((col) => (
                      <th key={col}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row, idx) => (
                    <tr key={idx}>
                      {result.columns.map((col) => (
                        <td key={col}>{String(row[col] ?? "-")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <h2 className="policy-section-title" style={{ marginTop: 32 }}>질의 이력</h2>

      {logsLoading ? (
        <p>불러오는 중...</p>
      ) : (
        <>
          <table className="admin-table">
            <thead>
              <tr>
                <th>일시</th>
                <th>질문</th>
                <th>상태</th>
                <th>응답시간</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.log_id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>{log.question_text}</td>
                  <td>
                    <span style={{ color: STATUS_COLOR[log.execution_status] }}>
                      {STATUS_LABEL[log.execution_status] ?? log.execution_status}
                    </span>
                  </td>
                  <td>{log.response_time_ms}ms</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: "center", color: "#9ca3af" }}>
                    질의 이력이 없습니다.
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

export default SqlAgentPage;