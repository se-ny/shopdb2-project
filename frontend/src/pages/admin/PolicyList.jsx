import { useEffect, useState } from "react";
import { fetchCompanyPolicies, fetchRefundPolicies, expireCompanyPolicy, expireRefundPolicy } from "../../api/admin";
import CompanyPolicyForm from "./CompanyPolicyForm";
import RefundPolicyForm from "./RefundPolicyForm";

function PolicyList() {
  const [companyPolicies, setCompanyPolicies] = useState([]);
  const [refundPolicies, setRefundPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [showCompanyForm, setShowCompanyForm] = useState(false);
  const [showRefundForm, setShowRefundForm] = useState(false);
  const [editingCompanyPolicy, setEditingCompanyPolicy] = useState(null);
  const [editingRefundPolicy, setEditingRefundPolicy] = useState(null);

  function loadAll() {
    setLoading(true);
    Promise.all([fetchCompanyPolicies(), fetchRefundPolicies()])
      .then(([company, refund]) => {
        setCompanyPolicies(company);
        setRefundPolicies(refund);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleExpireCompany(policyId) {
    if (!confirm("이 정책을 만료 처리하시겠습니까?")) return;
    await expireCompanyPolicy(policyId);
    loadAll();
  }

  async function handleExpireRefund(refundPolicyId) {
    if (!confirm("이 환불정책을 만료 처리하시겠습니까?")) return;
    await expireRefundPolicy(refundPolicyId);
    loadAll();
  }

  function handleEditCompany(policy) {
    setEditingCompanyPolicy(policy);
    setShowCompanyForm(true);
  }

  function handleEditRefund(policy) {
    setEditingRefundPolicy(policy);
    setShowRefundForm(true);
  }

  function handleAddCompany() {
    setEditingCompanyPolicy(null);
    setShowCompanyForm(true);
  }

  function handleAddRefund() {
    setEditingRefundPolicy(null);
    setShowRefundForm(true);
  }

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <h1>정책 관리</h1>

      <div className="admin-page-header">
        <h2 className="policy-section-title">이용약관 (company_policies)</h2>
        {!showCompanyForm && <button onClick={handleAddCompany}>+ 새 버전 등록</button>}
      </div>
      {showCompanyForm && (
        <CompanyPolicyForm
          editingPolicy={editingCompanyPolicy}
          onSaved={() => { setShowCompanyForm(false); setEditingCompanyPolicy(null); loadAll(); }}
          onCancel={() => { setShowCompanyForm(false); setEditingCompanyPolicy(null); }}
        />
      )}
      <table className="admin-table">
        <thead>
          <tr>
            <th>정책코드</th><th>정책명</th><th>버전</th><th>시행일</th><th>종료일</th><th>상태</th><th>동작</th>
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
              <td>
                <button onClick={() => handleEditCompany(policy)}>수정</button>
                {policy.active_yn === "Y" && (
                  <button onClick={() => handleExpireCompany(policy.policy_id)}>만료처리</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="admin-page-header">
        <h2 className="policy-section-title">환불정책 (refund_policies)</h2>
        {!showRefundForm && <button onClick={handleAddRefund}>+ 새 버전 등록</button>}
      </div>
      {showRefundForm && (
        <RefundPolicyForm
          editingPolicy={editingRefundPolicy}
          onSaved={() => { setShowRefundForm(false); setEditingRefundPolicy(null); loadAll(); }}
          onCancel={() => { setShowRefundForm(false); setEditingRefundPolicy(null); }}
        />
      )}
      <table className="admin-table">
        <thead>
          <tr>
            <th>정책명</th><th>허용일수</th><th>미개봉환불</th><th>개봉환불</th><th>불량환불</th><th>배송비부담</th><th>시행일</th><th>상태</th><th>동작</th>
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
              <td>
                <button onClick={() => handleEditRefund(policy)}>수정</button>
                {policy.active_yn === "Y" && (
                  <button onClick={() => handleExpireRefund(policy.refund_policy_id)}>만료처리</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PolicyList;