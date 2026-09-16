import { useState } from "react";
import { updateUser, assignRole, removeRole } from "../../api/admin";

const STATUS_OPTIONS = ["ACTIVE", "INACTIVE", "SUSPENDED", "WITHDRAWN"];

function UserEditPanel({ user, allRoles, onSaved, onCancel }) {
  const [orgId, setOrgId] = useState(user.org_id ?? "");
  const [status, setStatus] = useState(user.user_status);
  const currentRoleIds = user.roles.map((r) => r.role_id);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSave() {
    setSaving(true);
    setErrorMessage("");
    try {
      await updateUser(user.user_id, {
        org_id: orgId ? Number(orgId) : null,
        user_status: status,
      });
      onSaved();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleRole(roleId, isAssigned) {
    setSaving(true);
    setErrorMessage("");
    try {
      if (isAssigned) {
        await removeRole(user.user_id, roleId);
      } else {
        await assignRole(user.user_id, roleId);
      }
      onSaved();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="admin-form">
      <h2>{user.user_name} ({user.login_id}) 수정</h2>

      <label>
        소속 조직 ID
        <input type="number" value={orgId} onChange={(e) => setOrgId(e.target.value)} />
      </label>

      <label>
        상태
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {STATUS_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <div>
        <p style={{ marginBottom: 6 }}>역할</p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {allRoles.map((role) => {
            const isAssigned = currentRoleIds.includes(role.role_id);
            return (
              <label key={role.role_id} style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
                <input
                  type="checkbox"
                  checked={isAssigned}
                  disabled={saving}
                  onChange={() => handleToggleRole(role.role_id, isAssigned)}
                />
                {role.role_code}
              </label>
            );
          })}
        </div>
      </div>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button onClick={handleSave} disabled={saving}>
          {saving ? "저장 중..." : "상태/조직 저장"}
        </button>
        <button type="button" onClick={onCancel} disabled={saving}>
          닫기
        </button>
      </div>
    </div>
  );
}

export default UserEditPanel;