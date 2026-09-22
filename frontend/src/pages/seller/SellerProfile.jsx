import { useEffect, useState } from "react";
import {
  getSellerProfile,
  updateSellerProfile,
} from "../../api/sellerProfile";

export default function SellerProfile() {
  const [sellerUserId, setSellerUserId] =
    useState(2);

  const [profile, setProfile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadProfile(userId) {
    try {
      setLoading(true);
      setError("");
      setMessage("");

      const data = await getSellerProfile(
        userId,
      );

      setProfile(data);
    } catch (err) {
      setError(
        err.message ||
          "판매자 정보를 불러오지 못했습니다.",
      );

      setProfile(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfile(sellerUserId);
  }, [sellerUserId]);

  function handleChange(event) {
    const { name, value } = event.target;

    setProfile((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSave(event) {
    event.preventDefault();

    if (!profile) {
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMessage("");

      const updated =
        await updateSellerProfile(
          sellerUserId,
          {
            company_name:
              profile.company_name,
            business_number:
              profile.business_number || null,
            representative_name:
              profile.representative_name ||
              null,
            settlement_bank:
              profile.settlement_bank || null,
            settlement_account:
              profile.settlement_account ||
              null,
            seller_status:
              profile.seller_status,
          },
        );

      setProfile(updated);

      setMessage(
        "판매자 정보가 수정되었습니다.",
      );
    } catch (err) {
      setError(
        err.message ||
          "판매자 정보 수정에 실패했습니다.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "24px",
      }}
    >
      <div
        style={{
          marginBottom: "24px",
        }}
      >
        <p>SHOPDB2 SELLER</p>
        <h1>판매자 정보 관리</h1>
      </div>

      <label>
        판매자 선택

        <select
          value={sellerUserId}
          onChange={(event) =>
            setSellerUserId(
              Number(event.target.value),
            )
          }
          style={{
            marginLeft: "10px",
            padding: "8px",
          }}
        >
          <option value={2}>
            전자판매자
          </option>

          <option value={3}>
            패션판매자
          </option>
        </select>
      </label>

      {loading && (
        <p>판매자 정보를 불러오는 중입니다.</p>
      )}

      {error && (
        <p
          style={{
            color: "red",
          }}
        >
          {error}
        </p>
      )}

      {message && (
        <p>{message}</p>
      )}

      {!loading && profile && (
        <form
          onSubmit={handleSave}
          style={{
            display: "grid",
            gap: "16px",
            marginTop: "24px",
            padding: "24px",
            border: "1px solid #dddddd",
            borderRadius: "12px",
          }}
        >
          <p>
            판매자 ID: {profile.seller_id}
          </p>

          <p>
            사용자 ID: {profile.user_id}
          </p>

          <label>
            회사명

            <input
              type="text"
              name="company_name"
              value={
                profile.company_name || ""
              }
              onChange={handleChange}
            />
          </label>

          <label>
            사업자번호

            <input
              type="text"
              name="business_number"
              value={
                profile.business_number || ""
              }
              onChange={handleChange}
            />
          </label>

          <label>
            대표자명

            <input
              type="text"
              name="representative_name"
              value={
                profile.representative_name ||
                ""
              }
              onChange={handleChange}
            />
          </label>

          <label>
            정산 은행

            <input
              type="text"
              name="settlement_bank"
              value={
                profile.settlement_bank || ""
              }
              onChange={handleChange}
            />
          </label>

          <label>
            정산 계좌

            <input
              type="text"
              name="settlement_account"
              value={
                profile.settlement_account ||
                ""
              }
              onChange={handleChange}
            />
          </label>

          <label>
            판매자 상태

            <select
              name="seller_status"
              value={
                profile.seller_status || ""
              }
              onChange={handleChange}
            >
              <option value="ACTIVE">
                활성
              </option>

              <option value="INACTIVE">
                비활성
              </option>

              <option value="SUSPENDED">
                정지
              </option>
            </select>
          </label>

          <button
            type="submit"
            disabled={saving}
          >
            {saving
              ? "저장 중..."
              : "판매자 정보 저장"}
          </button>
        </form>
      )}
    </section>
  );
}