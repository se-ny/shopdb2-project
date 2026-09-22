import { useState } from "react";
import { createCompanyPolicy, updateCompanyPolicy } from "../../api/admin";

function CompanyPolicyForm({ editingPolicy, onSaved, onCancel }) {
  const isEdit = !!editingPolicy;

  const [form, setForm] = useState({
    policy_code: editingPolicy?.policy_code ?? "",
    policy_name: editingPolicy?.policy_name ?? "",
    policy_version: editingPolicy?.policy_version ?? "",
    policy_type: editingPolicy?.policy_type ?? "TERMS",
    policy_content: editingPolicy?.policy_content ?? "",
    effective_from: editingPolicy?.effective_from ?? "",
    effective_to: editingPolicy?.effective_to ?? "",
    org_id: editingPolicy?.org_id ?? "",
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
      if (isEdit) {
        await updateCompanyPolicy(editingPolicy.policy_id, {
          policy_name: form.policy_name,
          policy_version: form.policy_version,
          policy_type: form.policy_type,
          policy_content: form.policy_content,
          effective_from: form.effective_from,
          effective_to: form.effective_to || null,
        });
      } else {
        await createCompanyPolicy({
          ...form,
          effective_to: form.effective_to || null,
          org_id: form.org_id ? Number(form.org_id) : null,
        });
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
      <h2>{isEdit ? "이용약관 수정" : "이용약관 새 버전 등록"}</h2>
      <label>
        정책코드
        <input
          value={form.policy_code}
          onChange={(e) => handleChange("policy_code", e.target.value)}
          required
          disabled={isEdit}
        />
      </label>
      <label>
        정책명
        <input value={form.policy_name} onChange={(e) => handleChange("policy_name", e.target.value)} required />
      </label>
      <label>
        버전
        <input
          value={form.policy_version}
          onChange={(e) => handleChange("policy_version", e.target.value)}
          placeholder="예: 2027.1"
          required
        />
      </label>
      <label>
        정책 유형
        <input
          value={form.policy_type}
          onChange={(e) => handleChange("policy_type", e.target.value)}
          placeholder="예: TERMS, PRIVACY"
        />
      </label>
      {!isEdit && (
        <label>
          적용 조직 ID (비워두면 전사 공통)
          <input
            type="number"
            value={form.org_id}
            onChange={(e) => handleChange("org_id", e.target.value)}
          />
        </label>
      )}
      <label>
        내용
        <input value={form.policy_content} onChange={(e) => handleChange("policy_content", e.target.value)} />
      </label>
      <label>
        시행일
        <input type="date" value={form.effective_from} onChange={(e) => handleChange("effective_from", e.target.value)} required />
      </label>
      <label>
        종료일 (없으면 비워두세요)
        <input type="date" value={form.effective_to} onChange={(e) => handleChange("effective_to", e.target.value)} />
      </label>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>{saving ? "저장 중..." : isEdit ? "수정 저장" : "등록"}</button>
        <button type="button" onClick={onCancel} disabled={saving}>취소</button>
      </div>
    </form>
  );
}

export default CompanyPolicyForm;