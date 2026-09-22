import { useState } from "react";
import { createRefundPolicy } from "../../api/admin";

function RefundPolicyForm({ onSaved, onCancel }) {
  const [form, setForm] = useState({
    policy_name: "",
    allowed_days: 7,
    unopened_refund_yn: "Y",
    opened_refund_yn: "N",
    defective_refund_yn: "Y",
    shipping_fee_payer: "BUYER",
    refund_policy_text: "",
    effective_from: "",
    org_id: "",
  });
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function handleChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleCheckbox(field, checked) {
    setForm((prev) => ({ ...prev, [field]: checked ? "Y" : "N" }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setErrorMessage("");
    try {
      await createRefundPolicy({
        ...form,
        allowed_days: Number(form.allowed_days),
        org_id: form.org_id ? Number(form.org_id) : null,
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
      <h2>환불정책 새 버전 등록</h2>
      <label>
        정책명
        <input value={form.policy_name} onChange={(e) => handleChange("policy_name", e.target.value)} required />
      </label>
      <label>
        허용일수
        <input type="number" value={form.allowed_days} onChange={(e) => handleChange("allowed_days", e.target.value)} required />
      </label>
      <label>
        적용 조직 ID (비워두면 전사 공통)
        <input
          type="number"
          value={form.org_id}
          onChange={(e) => handleChange("org_id", e.target.value)}
        />
      </label>

      <label style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
        <input
          type="checkbox"
          checked={form.unopened_refund_yn === "Y"}
          onChange={(e) => handleCheckbox("unopened_refund_yn", e.target.checked)}
        />
        미개봉 상품 환불 허용
      </label>
      <label style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
        <input
          type="checkbox"
          checked={form.opened_refund_yn === "Y"}
          onChange={(e) => handleCheckbox("opened_refund_yn", e.target.checked)}
        />
        개봉 상품 환불 허용
      </label>
      <label style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
        <input
          type="checkbox"
          checked={form.defective_refund_yn === "Y"}
          onChange={(e) => handleCheckbox("defective_refund_yn", e.target.checked)}
        />
        불량품 환불 허용
      </label>

      <label>
        배송비 부담
        <select value={form.shipping_fee_payer} onChange={(e) => handleChange("shipping_fee_payer", e.target.value)}>
          <option value="BUYER">BUYER</option>
          <option value="SELLER">SELLER</option>
          <option value="COMPANY">COMPANY</option>
        </select>
      </label>
      <label>
        정책 설명
        <input value={form.refund_policy_text} onChange={(e) => handleChange("refund_policy_text", e.target.value)} />
      </label>
      <label>
        시행일
        <input type="date" value={form.effective_from} onChange={(e) => handleChange("effective_from", e.target.value)} required />
      </label>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>{saving ? "저장 중..." : "등록"}</button>
        <button type="button" onClick={onCancel} disabled={saving}>취소</button>
      </div>
    </form>
  );
}

export default RefundPolicyForm;