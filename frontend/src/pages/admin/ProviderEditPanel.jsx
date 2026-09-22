import { useState } from "react";
import { updateProvider } from "../../api/admin";

function ProviderEditPanel({ provider, onSaved, onCancel }) {
  const [form, setForm] = useState({
    provider_name: provider.provider_name,
    base_url: provider.base_url ?? "",
    chat_model: provider.chat_model ?? "",
    embedding_model: provider.embedding_model ?? "",
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
      await updateProvider(provider.provider_id, form);
      onSaved();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="admin-form">
      <h2>{provider.provider_code} 수정</h2>
      <label>
        Provider 이름
        <input value={form.provider_name} onChange={(e) => handleChange("provider_name", e.target.value)} required />
      </label>
      <label>
        Base URL
        <input value={form.base_url} onChange={(e) => handleChange("base_url", e.target.value)} />
      </label>
      <label>
        채팅 모델
        <input value={form.chat_model} onChange={(e) => handleChange("chat_model", e.target.value)} />
      </label>
      <label>
        임베딩 모델
        <input value={form.embedding_model} onChange={(e) => handleChange("embedding_model", e.target.value)} />
      </label>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>{saving ? "저장 중..." : "저장"}</button>
        <button type="button" onClick={onCancel} disabled={saving}>취소</button>
      </div>
    </form>
  );
}

export default ProviderEditPanel;