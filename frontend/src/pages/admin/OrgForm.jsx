import { useState } from "react";
import { createOrg, updateOrg } from "../../api/admin";

const ORG_TYPES = ["HEADQUARTER", "BRANCH", "STORE", "WAREHOUSE"];

function OrgForm({ editingOrg, onSaved, onCancel }) {
  const [form, setForm] = useState({
    org_code: editingOrg?.org_code ?? "",
    org_name: editingOrg?.org_name ?? "",
    org_type: editingOrg?.org_type ?? "BRANCH",
    parent_org_id: editingOrg?.parent_org_id ?? "",
    representative_name: editingOrg?.representative_name ?? "",
    phone: editingOrg?.phone ?? "",
    email: editingOrg?.email ?? "",
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
      const payload = {
        ...form,
        parent_org_id: form.parent_org_id ? Number(form.parent_org_id) : null,
      };
      if (editingOrg) {
        await updateOrg(editingOrg.org_id, payload);
      } else {
        await createOrg(payload);
      }
      onSaved();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="admin-form">
      <h2>{editingOrg ? "조직 수정" : "조직 등록"}</h2>

      <label>
        조직코드
        <input
          value={form.org_code}
          onChange={(e) => handleChange("org_code", e.target.value)}
          required
          disabled={!!editingOrg}
        />
      </label>

      <label>
        조직명
        <input
          value={form.org_name}
          onChange={(e) => handleChange("org_name", e.target.value)}
          required
        />
      </label>

      <label>
        구분
        <select value={form.org_type} onChange={(e) => handleChange("org_type", e.target.value)}>
          {ORG_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </label>

      <label>
        상위 조직 ID (본사면 비워두세요)
        <input
          type="number"
          value={form.parent_org_id}
          onChange={(e) => handleChange("parent_org_id", e.target.value)}
        />
      </label>

      <label>
        대표자명
        <input
          value={form.representative_name}
          onChange={(e) => handleChange("representative_name", e.target.value)}
        />
      </label>

      <label>
        전화번호
        <input value={form.phone} onChange={(e) => handleChange("phone", e.target.value)} />
      </label>

      <label>
        이메일
        <input value={form.email} onChange={(e) => handleChange("email", e.target.value)} />
      </label>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>
          {saving ? "저장 중..." : "저장"}
        </button>
        <button type="button" onClick={onCancel} disabled={saving}>
          취소
        </button>
      </div>
    </form>
  );
}

export default OrgForm;