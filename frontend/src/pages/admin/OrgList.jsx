import { useEffect, useState } from "react";
import { fetchOrgs, deactivateOrg, activateOrg } from "../../api/admin";
import OrgForm from "./OrgForm";

function OrgList() {
  const [orgs, setOrgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingOrg, setEditingOrg] = useState(null);

  function loadOrgs() {
    setLoading(true);
    fetchOrgs()
      .then(setOrgs)
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadOrgs();
  }, []);

  function handleAddClick() {
    setEditingOrg(null);
    setShowForm(true);
  }

  function handleEditClick(org) {
    setEditingOrg(org);
    setShowForm(true);
  }

  function handleSaved() {
    setShowForm(false);
    setEditingOrg(null);
    loadOrgs();
  }

  async function handleDeactivate(org) {
    if (!confirm(`${org.org_name}을(를) 비활성화하시겠습니까?`)) return;
    try {
      await deactivateOrg(org.org_id);
      loadOrgs();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  async function handleActivate(org) {
    if (!confirm(`${org.org_name}을(를) 다시 활성화하시겠습니까?`)) return;
    try {
      await activateOrg(org.org_id);
      loadOrgs();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <div className="admin-page-header">
        <h1>조직관리</h1>
        {!showForm && <button onClick={handleAddClick}>+ 조직 등록</button>}
      </div>

      {showForm && (
        <OrgForm
          editingOrg={editingOrg}
          onSaved={handleSaved}
          onCancel={() => setShowForm(false)}
        />
      )}

      <table className="admin-table">
        <thead>
          <tr>
            <th>조직코드</th>
            <th>조직명</th>
            <th>구분</th>
            <th>대표자</th>
            <th>상태</th>
            <th>동작</th>
          </tr>
        </thead>
        <tbody>
          {orgs.map((org) => (
            <tr key={org.org_id}>
              <td>{org.org_code}</td>
              <td>{org.org_name}</td>
              <td>{org.org_type}</td>
              <td>{org.representative_name}</td>
              <td>{org.active_yn === "Y" ? "활성" : "비활성"}</td>
              <td>
                <button onClick={() => handleEditClick(org)}>수정</button>
                {org.active_yn === "Y" ? (
                  <button onClick={() => handleDeactivate(org)}>비활성화</button>
                ) : (
                  <button onClick={() => handleActivate(org)}>활성화</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default OrgList;