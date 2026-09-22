import { useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function LoginPage() {
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const buyerReturn = location.state?.buyerReturn || null;

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await login(loginId, password);

      if (result.roles.includes("ADMIN")) {
        navigate("/admin/orgs", { replace: true });
        return;
      }

      navigate("/", {
        replace: true,
        state: buyerReturn ? { buyerReturn } : null,
      });
    } catch (err) {
      setError(
        err.message || "로그인에 실패했습니다. 아이디와 비밀번호를 확인해 주세요.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: "80px auto", padding: 24 }}>
      <h1 style={{ marginBottom: 12 }}>SHOPDB2 로그인</h1>

      {buyerReturn && (
        <p style={{ margin: "0 0 24px", color: "#525252", lineHeight: 1.6 }}>
          장바구니, 주문 등 구매 기능을 이용하려면 로그인이 필요합니다.
          로그인 후 이전 화면으로 돌아갑니다.
        </p>
      )}

      <form onSubmit={handleSubmit} className="admin-form">
        <label>
          아이디
          <input
            value={loginId}
            onChange={(e) => setLoginId(e.target.value)}
            required
          />
        </label>

        <label>
          비밀번호
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "로그인 중..." : "로그인"}
        </button>
      </form>
    </div>
  );
}

export default LoginPage;
