import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createRawRow,
  deleteRawRow,
  fetchRawRows,
  fetchRawSchema,
  fetchRawTables,
  updateRawRow,
} from "../../api/admin";

const PAGE_SIZE = 30;

function stringifyValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function normalizeInput(value) {
  return value === "" ? null : value;
}

function AdminDataManager() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [schema, setSchema] = useState(null);
  const [rows, setRows] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [formMode, setFormMode] = useState("");
  const [formState, setFormState] = useState({});
  const [selectedRow, setSelectedRow] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const columns = schema?.columns ?? [];
  const primaryKeys = schema?.primary_keys ?? [];
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const loadTables = useCallback(async () => {
    try {
      setError("");
      const data = await fetchRawTables();
      setTables(data.tables ?? []);
      if (!selectedTable && data.tables?.length) {
        setSelectedTable(data.tables[0]);
      }
    } catch (err) {
      setError(err.message);
    }
  }, [selectedTable]);

  const loadTable = useCallback(async () => {
    if (!selectedTable) return;
    setLoading(true);
    setError("");
    try {
      const [schemaData, rowData] = await Promise.all([
        fetchRawSchema(selectedTable),
        fetchRawRows(selectedTable, page, PAGE_SIZE),
      ]);
      setSchema(schemaData);
      setRows(rowData.rows ?? []);
      setTotal(rowData.total ?? 0);
      setSelectedRow(null);
      setFormMode("");
      setFormState({});
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedTable, page]);

  useEffect(() => {
    loadTables();
  }, [loadTables]);

  useEffect(() => {
    loadTable();
  }, [loadTable]);

  const editableColumns = useMemo(
    () => columns.filter((column) => !(formMode === "create" && column.auto_increment)),
    [columns, formMode]
  );

  function startCreate() {
    const initial = {};
    columns.forEach((column) => {
      if (!column.auto_increment) initial[column.name] = "";
    });
    setSelectedRow(null);
    setFormState(initial);
    setFormMode("create");
    setMessage("");
    setError("");
  }

  function startEdit(row) {
    const initial = {};
    columns.forEach((column) => {
      initial[column.name] = stringifyValue(row[column.name]);
    });
    setSelectedRow(row);
    setFormState(initial);
    setFormMode("edit");
    setMessage("");
    setError("");
  }

  function pkOf(row) {
    return Object.fromEntries(primaryKeys.map((key) => [key, row[key]]));
  }

  async function saveForm(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const values = Object.fromEntries(
        Object.entries(formState).map(([key, value]) => [key, normalizeInput(value)])
      );
      if (formMode === "create") {
        await createRawRow(selectedTable, values);
        setMessage("새 행을 생성했습니다.");
      } else {
        await updateRawRow(selectedTable, pkOf(selectedRow), values);
        setMessage("행을 수정했습니다.");
      }
      setFormMode("");
      await loadTable();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function removeRow(row) {
    if (!primaryKeys.length) {
      setError("PK가 없는 테이블은 안전한 삭제를 지원하지 않습니다.");
      return;
    }
    const label = primaryKeys.map((key) => `${key}=${row[key]}`).join(", ");
    if (!window.confirm(`${selectedTable} (${label}) 행을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`)) {
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await deleteRawRow(selectedTable, pkOf(row));
      setMessage("행을 삭제했습니다.");
      await loadTable();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <div>
          <h2 style={{ marginBottom: 6 }}>원본데이터 관리</h2>
          <p style={{ color: "#64748b", marginTop: 0 }}>
            shopdb2의 실제 테이블 데이터를 관리자 권한으로 조회·등록·수정·삭제합니다.
          </p>
        </div>
        <button type="button" onClick={startCreate} disabled={!selectedTable || loading}>
          + 새 행
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "240px minmax(0, 1fr)", gap: 18 }}>
        <aside style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: 12, maxHeight: "70vh", overflow: "auto" }}>
          <strong>테이블 {tables.length}개</strong>
          <div style={{ display: "grid", gap: 4, marginTop: 10 }}>
            {tables.map((table) => (
              <button
                key={table}
                type="button"
                onClick={() => {
                  setPage(1);
                  setSelectedTable(table);
                }}
                style={{
                  textAlign: "left",
                  padding: "8px 10px",
                  border: "1px solid #e5e7eb",
                  borderRadius: 6,
                  background: selectedTable === table ? "#dbeafe" : "#fff",
                  cursor: "pointer",
                }}
              >
                {table}
              </button>
            ))}
          </div>
        </aside>

        <section style={{ minWidth: 0 }}>
          {error && <p style={{ padding: 12, background: "#fef2f2", color: "#b91c1c", borderRadius: 8 }}>{error}</p>}
          {message && <p style={{ padding: 12, background: "#f0fdf4", color: "#166534", borderRadius: 8 }}>{message}</p>}

          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", marginBottom: 10 }}>
            <strong>{selectedTable || "테이블 선택"}</strong>
            <span>행 {total}개</span>
            <span>PK: {primaryKeys.length ? primaryKeys.join(", ") : "없음"}</span>
            <button type="button" onClick={loadTable} disabled={loading}>새로고침</button>
          </div>

          <div style={{ overflow: "auto", border: "1px solid #e5e7eb", borderRadius: 10 }}>
            <table style={{ borderCollapse: "collapse", width: "max-content", minWidth: "100%" }}>
              <thead>
                <tr>
                  {columns.map((column) => (
                    <th key={column.name} style={{ padding: 9, borderBottom: "1px solid #e5e7eb", textAlign: "left", background: "#f8fafc" }}>
                      {column.name}
                      {column.primary_key ? " 🔑" : ""}
                    </th>
                  ))}
                  <th style={{ padding: 9, background: "#f8fafc" }}>관리</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={primaryKeys.map((key) => row[key]).join("|") || index}>
                    {columns.map((column) => (
                      <td key={column.name} style={{ padding: 9, borderBottom: "1px solid #f1f5f9", maxWidth: 280 }}>
                        <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={stringifyValue(row[column.name])}>
                          {row[column.name] === null ? "NULL" : stringifyValue(row[column.name])}
                        </div>
                      </td>
                    ))}
                    <td style={{ padding: 9, borderBottom: "1px solid #f1f5f9", whiteSpace: "nowrap" }}>
                      <button type="button" onClick={() => startEdit(row)} disabled={!primaryKeys.length}>수정</button>{" "}
                      <button type="button" onClick={() => removeRow(row)} disabled={!primaryKeys.length}>삭제</button>
                    </td>
                  </tr>
                ))}
                {!rows.length && !loading && (
                  <tr><td colSpan={columns.length + 1} style={{ padding: 24, textAlign: "center" }}>데이터가 없습니다.</td></tr>
                )}
              </tbody>
            </table>
          </div>

          <div style={{ display: "flex", justifyContent: "center", gap: 10, marginTop: 14 }}>
            <button type="button" disabled={page <= 1 || loading} onClick={() => setPage((value) => value - 1)}>이전</button>
            <span>{page} / {pageCount}</span>
            <button type="button" disabled={page >= pageCount || loading} onClick={() => setPage((value) => value + 1)}>다음</button>
          </div>
        </section>
      </div>

      {formMode && (
        <div style={{ position: "fixed", inset: 0, zIndex: 1200, background: "rgba(15,23,42,.55)", display: "grid", placeItems: "center", padding: 20 }}>
          <form onSubmit={saveForm} style={{ width: "min(760px, 100%)", maxHeight: "90vh", overflow: "auto", background: "#fff", borderRadius: 14, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <div>
                <h3 style={{ margin: 0 }}>{formMode === "create" ? "새 행 등록" : "행 수정"}</h3>
                <p>{selectedTable}</p>
              </div>
              <button type="button" onClick={() => setFormMode("")}>닫기</button>
            </div>

            <div style={{ display: "grid", gap: 12 }}>
              {editableColumns.map((column) => (
                <label key={column.name} style={{ display: "grid", gap: 5 }}>
                  <span>
                    <strong>{column.name}</strong>{" "}
                    <small>
                      {column.column_type}
                      {column.primary_key ? " · PK" : ""}
                      {column.nullable ? " · NULL 허용" : " · 필수"}
                    </small>
                  </span>
                  <textarea
                    rows={column.data_type === "text" || column.data_type === "longtext" || column.data_type === "json" ? 4 : 1}
                    value={formState[column.name] ?? ""}
                    onChange={(event) => setFormState((current) => ({ ...current, [column.name]: event.target.value }))}
                    disabled={formMode === "edit" && column.primary_key}
                    placeholder={column.default !== null && column.default !== undefined ? `기본값: ${column.default}` : ""}
                    style={{ padding: 9, resize: "vertical" }}
                  />
                </label>
              ))}
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 18 }}>
              <button type="button" onClick={() => setFormMode("")}>취소</button>
              <button type="submit" disabled={loading}>{loading ? "저장 중..." : "저장"}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default AdminDataManager;
