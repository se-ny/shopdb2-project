import { useState } from "react";
import { createDocument } from "../../api/admin";

const SOURCE_TYPES = ["DATABASE", "FILE", "URL", "API", "MANUAL"];

function DocumentForm({ providers, onSaved, onCancel }) {
  const [form, setForm] = useState({
    document_name: "",
    document_type: "",
    source_type: "MANUAL",
    source_uri: "",
    content_text: "",
    version: "",
    provider_id: providers[0]?.provider_id ?? "",
    org_id: "",
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
      await createDocument({
        ...form,
        provider_id: form.provider_id ? Number(form.provider_id) : null,
        org_id: form.org_id ? Number(form.org_id) : null,
      });
      onSaved();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="admin-form">
      <h2>문서 등록</h2>

      <label>
        문서명
        <input value={form.document_name} onChange={(e) => handleChange("document_name", e.target.value)} required />
      </label>

      <label>
        문서 종류 (예: REFUND_POLICY, PRODUCT_GUIDE)
        <input value={form.document_type} onChange={(e) => handleChange("document_type", e.target.value)} />
      </label>

      <label>
        출처 유형
        <select value={form.source_type} onChange={(e) => handleChange("source_type", e.target.value)}>
          {SOURCE_TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </label>

      <label>
        Provider
        <select value={form.provider_id} onChange={(e) => handleChange("provider_id", e.target.value)}>
          {providers.map((p) => (
            <option key={p.provider_id} value={p.provider_id}>{p.provider_code}</option>
          ))}
        </select>
      </label>

      <label>
        소속 조직 ID (선택)
        <input type="number" value={form.org_id} onChange={(e) => handleChange("org_id", e.target.value)} />
      </label>

      <label>
        버전
        <input value={form.version} onChange={(e) => handleChange("version", e.target.value)} placeholder="예: 2027.1" />
      </label>

      <label>
        내용 (문서 원문)
        <textarea
          value={form.content_text}
          onChange={(e) => handleChange("content_text", e.target.value)}
          rows={4}
          required
        />
      </label>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>{saving ? "저장 중..." : "등록"}</button>
        <button type="button" onClick={onCancel} disabled={saving}>취소</button>
      </div>
    </form>
  );
}

export default DocumentForm;