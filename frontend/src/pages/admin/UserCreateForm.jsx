import { useState } from "react";
import { createUser } from "../../api/admin";

function UserCreateForm({ allRoles, onSaved, onCancel }) {
  const [form, setForm] = useState({
    login_id: "",
    password: "",
    user_name: "",
    email: "",
    phone: "",
    org_id: "",
  });
  const [selectedRoleIds, setSelectedRoleIds] = useState([]);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function handleChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function toggleRole(roleId) {
    setSelectedRoleIds((prev) =>
      prev.includes(roleId) ? prev.filter((id) => id !== roleId) : [...prev, roleId]
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setErrorMessage("");
    try {
      await createUser({
        ...form,
        org_id: form.org_id ? Number(form.org_id) : null,
        role_ids: selectedRoleIds,
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
      <h2>회원 등록</h2>
      <label>
        아이디
        <input value={form.login_id} onChange={(e) => handleChange("login_id", e.target.value)} required />
      </label>
      <label>
        비밀번호
        <input type="password" value={form.password} onChange={(e) => handleChange("password", e.target.value)} required />
      </label>
      <label>
        이름
        <input value={form.user_name} onChange={(e) => handleChange("user_name", e.target.value)} required />
      </label>
      <label>
        이메일
        <input type="email" value={form.email} onChange={(e) => handleChange("email", e.target.value)} required />
      </label>
      <label>
        전화번호
        <input value={form.phone} onChange={(e) => handleChange("phone", e.target.value)} />
      </label>
      <label>
        소속 조직 ID (선택)
        <input type="number" value={form.org_id} onChange={(e) => handleChange("org_id", e.target.value)} />
      </label>

      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        역할 (선택)
        {allRoles.map((role) => (
          <label key={role.role_id} style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
            <input
              type="checkbox"
              checked={selectedRoleIds.includes(role.role_id)}
              onChange={() => toggleRole(role.role_id)}
            />
            {role.role_code} ({role.role_name})
          </label>
        ))}
      </div>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>{saving ? "저장 중..." : "등록"}</button>
        <button type="button" onClick={onCancel} disabled={saving}>취소</button>
      </div>
    </form>
  );
}

export default UserCreateForm;