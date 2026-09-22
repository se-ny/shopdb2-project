import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router-dom";
import "../../styles/admin.css";
import { useAuth } from "../../context/AuthContext";

const MENU_ITEMS = [
  { to: "/admin/dashboard", label: "대시보드" },
  { to: "/admin/orgs", label: "조직관리" },
  { to: "/admin/orders", label: "주문관리" },
  { to: "/admin/products", label: "상품승인관리" },
  { to: "/admin/categories", label: "카테고리관리" },
  { to: "/admin/data", label: "원본데이터 관리" },
  { to: "/admin/users", label: "회원/권한" },
  { to: "/admin/policies", label: "정책관리" },
  { to: "/admin/payments", label: "결제/환불관리" },
  { to: "/admin/ai", label: "AI / RAG" },
  { to: "/admin/feedback", label: "AI 피드백" },
  { to: "/admin/sql-agent", label: "SQL 에이전트" },
  { to: "/admin/alerts", label: "시스템 알림" },
  { to: "/admin/logs", label: "활동로그" },
];

function AdminLayout() {
  const { auth, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <h2>관리자</h2>

        <p
          style={{
            fontSize: 13,
            color: "#9ca3af",
            marginTop: -8,
            marginBottom: 12,
          }}
        >
          {auth?.user_name}님
        </p>

        <nav>
          {MENU_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "active" : ""
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div
          style={{
            marginTop: 20,
            display: "grid",
            gap: 8,
          }}
        >
          <button
            type="button"
            onClick={() => navigate("/")}
          >
            ← SHOPDB2 홈
          </button>

          <button
            type="button"
            onClick={logout}
          >
            로그아웃
          </button>
        </div>
      </aside>

      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
}

export default AdminLayout;