import { useEffect, useState } from "react";
import { fetchCompanyPolicies, fetchRefundPolicies } from "../../api/admin";

function PolicyList() {
  const [companyPolicies, setCompanyPolicies] = useState([]);
  const [refundPolicies, setRefundPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    Promise.all([fetchCompanyPolicies(), fetchRefundPolicies()])
      .then(([company, refund]) => {
        setCompanyPolicies(company);
        setRefundPolicies(refund);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <h1>정책 관리</h1>

      <h2 className="policy-section-title">이용약관 (company_policies)</h2>
      <table className="admin-table">
        <thead>
          <tr>
            <th>정책코드</th>
            <th>정책명</th>
            <th>버전</th>
            <th>시행일</th>
            <th>종료일</th>
            <th>상태</th>
          </tr>
        </thead>
        <tbody>
          {companyPolicies.map((policy) => (
            <tr key={policy.policy_id}>
              <td>{policy.policy_code}</td>
              <td>{policy.policy_name}</td>
              <td>{policy.policy_version}</td>
              <td>{policy.effective_from}</td>
              <td>{policy.effective_to ?? "-"}</td>
              <td>{policy.active_yn === "Y" ? "활성" : "만료"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="policy-section-title">환불정책 (refund_policies)</h2>
      <table className="admin-table">
        <thead>
          <tr>
            <th>정책명</th>
            <th>허용일수</th>
            <th>미개봉환불</th>
            <th>개봉환불</th>
            <th>불량환불</th>
            <th>배송비부담</th>
            <th>시행일</th>
            <th>상태</th>
          </tr>
        </thead>
        <tbody>
          {refundPolicies.map((policy) => (
            <tr key={policy.refund_policy_id}>
              <td>{policy.policy_name}</td>
              <td>{policy.allowed_days}일</td>
              <td>{policy.unopened_refund_yn}</td>
              <td>{policy.opened_refund_yn}</td>
              <td>{policy.defective_refund_yn}</td>
              <td>{policy.shipping_fee_payer}</td>
              <td>{policy.effective_from}</td>
              <td>{policy.active_yn === "Y" ? "활성" : "만료"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PolicyList;