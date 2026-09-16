import { useEffect, useState } from "react";
import { fetchOrgs } from "../../api/admin";

function OrgList() {
  const [orgs, setOrgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchOrgs()
      .then(setOrgs)
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <h1>조직관리</h1>
      <table className="admin-table">
        <thead>
          <tr>
            <th>조직코드</th>
            <th>조직명</th>
            <th>구분</th>
            <th>대표자</th>
            <th>상태</th>
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default OrgList;