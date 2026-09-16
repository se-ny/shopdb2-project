import { useEffect, useState } from "react";
import { fetchUsers } from "../../api/admin";

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchUsers()
      .then(setUsers)
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <h1>회원/권한 관리</h1>
      <table className="admin-table">
        <thead>
          <tr>
            <th>아이디</th>
            <th>이름</th>
            <th>이메일</th>
            <th>소속 조직</th>
            <th>역할</th>
            <th>상태</th>
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default UserList;