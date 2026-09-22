import { useState } from "react";
import { updateDocument } from "../../api/admin";

function DocumentEditPanel({ document, onSaved, onCancel }) {
  const [form, setForm] = useState({
    document_name: document.document_name,
    document_type: document.document_type ?? "",
    content_text: document.content_text ?? "",
    version: document.version ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function handleChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setErrorMessage("");
    try {
      await updateDocument(document.document_id, form);
      onSaved();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="admin-form">
      <h2>{document.document_name} 수정</h2>
      <label>
        문서명
        <input value={form.document_name} onChange={(e) => handleChange("document_name", e.target.value)} required />
      </label>
      <label>
        문서 종류
        <input value={form.document_type} onChange={(e) => handleChange("document_type", e.target.value)} />
      </label>
      <label>
        버전
        <input value={form.version} onChange={(e) => handleChange("version", e.target.value)} />
      </label>
      <label>
        내용 (원문)
        <textarea
          value={form.content_text}
          onChange={(e) => handleChange("content_text", e.target.value)}
          rows={4}
        />
      </label>
      <p style={{ fontSize: 13, color: "#6b7280" }}>
        ⚠️ 내용을 바꾸면 기존 인덱싱 결과가 초기화됩니다. 저장 후 "인덱싱 실행"을 다시 눌러주세요.
      </p>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>{saving ? "저장 중..." : "저장"}</button>
        <button type="button" onClick={onCancel} disabled={saving}>취소</button>
      </div>
    </form>
  );
}

export default DocumentEditPanel;