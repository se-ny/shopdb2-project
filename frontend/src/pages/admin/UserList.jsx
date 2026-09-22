import { useEffect, useState } from "react";
import { fetchUsers, fetchRoles, withdrawUser } from "../../api/admin";
import UserEditPanel from "./UserEditPanel";
import UserCreateForm from "./UserCreateForm";

function UserList() {
  const [users, setUsers] = useState([]);
  const [allRoles, setAllRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [editingUserId, setEditingUserId] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  function loadAll() {
    setLoading(true);
    Promise.all([fetchUsers(), fetchRoles()])
      .then(([userData, roleData]) => {
        setUsers(userData);
        setAllRoles(roleData);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleWithdraw(user) {
    if (!confirm(`"${user.user_name}"님을 탈퇴 처리하시겠습니까?`)) return;
    try {
      await withdrawUser(user.user_id);
      loadAll();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  const editingUser = users.find((u) => u.user_id === editingUserId);

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <div className="admin-page-header">
        <h1>회원/권한 관리</h1>
        {!showCreateForm && <button onClick={() => setShowCreateForm(true)}>+ 회원 등록</button>}
      </div>

      {showCreateForm && (
        <UserCreateForm
          allRoles={allRoles}
          onSaved={() => { setShowCreateForm(false); loadAll(); }}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {editingUser && (
        <UserEditPanel
          user={editingUser}
          allRoles={allRoles}
          onSaved={loadAll}
          onCancel={() => setEditingUserId(null)}
        />
      )}

      <table className="admin-table">
        <thead>
          <tr>
            <th>아이디</th>
            <th>이름</th>
            <th>이메일</th>
            <th>소속 조직</th>
            <th>역할</th>
            <th>상태</th>
            <th>동작</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.user_id}>
              <td>{user.login_id}</td>
              <td>{user.user_name}</td>
              <td>{user.email}</td>
              <td>{user.org_id}</td>
              <td>
                {user.roles.map((role) => (
                  <span key={role.role_id} className="role-badge">
                    {role.role_code}
                  </span>
                ))}
              </td>
              <td>{user.user_status}</td>
              <td>
                <button onClick={() => setEditingUserId(user.user_id)}>수정</button>
                {user.user_status !== "WITHDRAWN" && (
                  <button onClick={() => handleWithdraw(user)}>탈퇴</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default UserList;